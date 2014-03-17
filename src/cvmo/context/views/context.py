import json
import pickle
import hashlib
import base64
import re
import urllib2
from passlib.hash import sha512_crypt
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.db.models import Q
from django.core.urlresolvers import reverse
from querystring_parser import parser
from cvmo.core.plugins import ContextPlugins
from cvmo.context.models import ContextStorage, ContextDefinition
from cvmo.core.utils.views import render_confirm, render_password_prompt, \
    render_error, uncache_response
from cvmo.core.utils.context import gen_context_key, salt_context_key, tou
from cvmo.core.utils import crypt

#
# Context creation
#


def blank(request):
    global _generic_plugin

    # Empty values
    values = {}

    # Render all of the plugins
    plugins = ContextPlugins().renderAll(request, values)

    # Append display property to every plugin, and set it to True
    for p in plugins:
        p['display'] = True

    # Render the response
    return render_to_response('context/context.html', {
        'cernvm': _get_cernvm_config(),
        'values': values,
        'disabled': False,
        'id': '',
        'plugins': plugins,
        'cernvm_plugin': _generic_plugin
    }, RequestContext(request))


def create(request):
    post_dict = parser.parse(
        unicode(request.POST.urlencode()).encode('utf-8'))

    # The values of all the plugins and the enabled plugins
    values = post_dict.get('values')
    enabled = post_dict.get('enabled')
    abstract = post_dict.get('abstract')

    # Generate a UUID for this context
    c_uuid = gen_context_key()

    # We need to generate hashes for passwords here: only on uCernVM for
    # compatibility reasons
    if 'cvm_version' in values['general'] \
            and values['general']['cvm_version'] == 'uCernVM':
        if 'users' in values['general']:
            for k, v in values['general']['users'].iteritems():
                # Don't re-hash (useful when cloning)
                if not str(v['password']).startswith('$6$'):
                    # rounds=5000 is used to avoid the $round=xxx$ placed into
                    # out string, see:
                    # http://pythonhosted.org/passlib/lib/passlib.hash.sha256_crypt.html
                    h = sha512_crypt.encrypt(
                        str(v['password']), salt_size=8, rounds=5000
                    )
                    values['general']['users'][k]['password'] = h

    # Collect data to save. Non-indexed data is pickled
    raw_values = {'values': values, 'enabled': enabled}
    if abstract is not None:
        raw_values['abstract'] = abstract
        from_abstract = True
    else:
        from_abstract = False

    # Prepare pickled data for easy reconstruction
    # (in case somebody wants to clone a template)
    c_values = pickle.dumps(raw_values)
    c_config = ContextPlugins().renderContext(c_uuid, values, enabled)

    # Generate checksum of the configuration
    c_checksum = hashlib.sha1(c_config).hexdigest()

    # Get the possible secret key
    c_key = ""
    if ('protect' in values) and (values['protect']):
        c_key = str(values['secret'])

    # If the content is encrypted process the data now
    if (c_key != ''):
        c_values = base64.b64encode(crypt.encrypt(c_values, c_key))
        c_config = "ENCRYPTED:" + \
            base64.b64encode(crypt.encrypt(c_config, c_key))
        c_key = salt_context_key(c_uuid, c_key)

    # Check if this is public
    c_public = False
    if ('public' in values) and (values['public']):
        c_public = True

    # Save context definition
    ContextDefinition.objects.create(
        id=c_uuid,
        name=tou(values['name']),
        description=tou(values['description']),
        owner=request.user,
        key=c_key,
        public=c_public,
        data=c_values,
        checksum=c_checksum,
        inherited=False,
        abstract=False,  # only True for pure abstract contexts
        from_abstract=from_abstract
    )

    # Save context data (Should go to key/value store for speed-up)
    ContextStorage.objects.create(
        id=c_uuid,
        data=c_config
    )

    # Go to dashboard
    return redirect('dashboard')

#
# Context cloning
#


def clone(request, context_id):
    global _generic_plugin

    # Fetch the entry from the db
    item = ContextDefinition.objects.get(id=context_id)
    data = {}

    # Check if the data are encrypted
    if item.key == '':
        data = pickle.loads(str(item.data))
    else:
        # Password-protected
        resp = _prompt_unencrypt_context(
            request, item,
            reverse('context_clone', kwargs={'context_id': context_id})
        )
        if 'httpresp' in resp:
            return resp['httpresp']
        elif 'data' in resp:
            data = pickle.loads(resp['data'])

    # Render all of the plugins
    plugins = ContextPlugins().renderAll(
        request, data['values'], data['enabled'])

    # Append display property to every plugin, and set it to True
    for p in plugins:
        p['display'] = True

    data['values']['name'] = _name_increment_revision(
        tou(data['values']['name']))

    # Render the response
    # raw = {'data':data}  # debug
    return render_to_response('context/context.html', {
        'cernvm': _get_cernvm_config(),
        'values': data['values'],
        'id': context_id,
        'disabled': False,
        #'raw': json.dumps(raw, indent=2),
        'plugins': plugins,
        'cernvm_plugin': _generic_plugin
    }, RequestContext(request))

#
# Removal of context
#


def delete(request, context_id):
    # Try to find the context
    try:
        context = ContextDefinition.objects.get(id=context_id)
    except:
        request.session["redirect_msg_error"] = "Context with id " + \
            context_id + " does not exist!"
        return redirect("dashboard")

    # Check if context belongs to calling user
    if request.user.id != context.owner.id:
        request.session["redirect_msg_error"] = "Context with id " + \
            context_id + " does not belong to you!"
        return redirect("dashboard")

    # Is it confirmed?
    if ('confirm' in request.GET) and (request.GET['confirm'] == 'yes'):
        # Delete the specified contextualization entry
        ContextDefinition.objects.filter(id=context_id).delete()

        # Go to dashboard
        request.session["redirect_msg_info"] = "Context removed successfully!"
        return redirect('dashboard')

    else:
        # Show the confirmation screen
        return render_confirm(
            request, 'Delete context',
            "Are you sure you want to delete this contextualization\
 information? This action is not undoable!",
            reverse('context_delete', kwargs={'context_id': context_id})
            + '?confirm=yes',
            reverse('dashboard')
        )

#
# Used from the webpage to show contexts. If encrypted, they interactively
# ask for a password
#


def view(request, context_id):
    global _generic_plugin

    # Fetch the entry from the db
    item = ContextDefinition.objects.get(id=context_id)
    data = {}

    # Check if the data are encrypted
    if item.key == '':
        data = pickle.loads(str(item.data))
    else:
        # Password-protected
        resp = _prompt_unencrypt_context(
            request, item,
            reverse('context_view', kwargs={'context_id': context_id})
        )
        if 'httpresp' in resp:
            return resp['httpresp']
        elif 'data' in resp:
            data = pickle.loads(resp['data'])

    # Render all of the plugins
    plugins = ContextPlugins().renderAll(
        request, data['values'], data['enabled'])

    # Append display property to every plugin, and set it to True
    for p in plugins:
        p['display'] = True

    # Render the response
    return render_to_response('context/context.html', {
        'cernvm': _get_cernvm_config(),
        'values': data['values'],
        'id': context_id,
        'disabled': True,
        'plugins': plugins,
        'cernvm_plugin': _generic_plugin
    }, RequestContext(request))


def api_get(request, context_id, format, askpass):
    """
    Returns the context definition in different formats and takes
    care of decrypting if requested
    """
    # 1. Retrieve the object from database
    try:
        ctx = ContextDefinition.objects.get(id=context_id)
    except ContextDefinition.DoesNotExist:
        return HttpResponse('not-found', content_type='text/plain')

    # Do we need to query ContextStorage?
    need_render = (format == 'raw' or format == 'plain')

    # Do we need to unmarshall data?
    need_data = (format == 'json')

    # Do we need to decrypt?
    if ctx.key:

        if askpass:
            # Prompt or decrypt
            resp = _prompt_unencrypt_context(request, ctx, '',
                                             decode_render=need_render)
            if 'httpresp' in resp:
                # Prompt
                return resp['httpresp']
            else:
                # Decrypt

                # When requested, data must be unpickled
                if need_data:
                    if not 'data' in resp:
                        return HttpResponse('db-error-data',
                                            content_type='text/plain')
                    else:
                        data = pickle.loads(resp['data'])

                # When requested, rendered part must be present
                if need_render:
                    if not 'render' in resp:
                        return HttpResponse('db-error-render',
                                            content_type='text/plain')
                    else:
                        render = resp['render']
        else:
            # Not asking for password: return encrypted data or nothing
            if format == 'json' or format == 'plain':
                return HttpResponse('encrypted', content_type='text/plain')
            elif format == 'raw':
                try:
                    stg = ContextStorage.objects.get(id=context_id)
                    render = stg.data
                except ContextStorage.DoesNotExist:
                    return HttpResponse('not-found-rendered-encrypted',
                                        content_type='text/plain')

    else:

        # Context is unencrypted
        if need_data:
            data = pickle.loads(str(ctx.data))
        if need_render:
            try:
                stg = ContextStorage.objects.get(id=context_id)
                render = stg.data
            except ContextStorage.DoesNotExist:
                return HttpResponse('not-found-rendered',
                                    content_type='text/plain')

    # Processing what we have, based on the desired output format
    if format == 'json':
        output = json.dumps(data, indent=2)
    elif format == 'raw':
        output = render
    elif format == 'plain':
        # Un-base64
        m = re.search(r'^\s*EC2_USER_DATA\s*=\s*([^\s]*)$', render, re.M)
        if m is None:
            return HttpResponse('render-format-error',
                                content_type='text/plain')
        try:
            output = base64.b64decode(m.group(1))
        except:
            return HttpResponse('render-encoding-error',
                                content_type='text/plain')

    return HttpResponse(output, content_type='text/plain')


def ajax_publish_context(request):
    """
    Changes the published value of a given context. Obtains all the parameters
    (id and action) through HTTP GET. Returns a HTTP status != 200 in case of
    errors, or an HTTP 200 with a JSON file containing the string '1' when OK
    """
    # id, do required
    if not 'do' in request.GET or not 'id' in request.GET:
        return render_error(request, 400, 'Action and/or id are missing')

    # Actions allowed: [un]publish
    if request.GET['do'] == 'publish':
        publish = True
    elif request.GET['do'] == 'unpublish':
        publish = False
    else:
        return render_error(request, 400, 'Invalid action')

    # Check if context exists and it's mine
    id = request.GET['id']
    ctx = ContextDefinition.objects.filter(
        Q(id=id) & Q(inherited=False) & Q(owner=request.user))
    if not ctx.exists or ctx.update(public=publish) != 1:
        return render_error(request, 500, 'Update error')

    # Will return the string '1' in case of success, '0' in case of failure
    return uncache_response(HttpResponse('1', content_type="application/json"))


#
# Helpers
#

# String corresponding to the generic plugin name
_generic_plugin = {
    'title': 'Basic CernVM configuration',
    'name': 'generic_cernvm',
    'display': True,
    'enabled': True
}


def _get_cernvm_config():
    """ Download the latest configuration parameters from CernVM """

    try:
        response = urllib2.urlopen('http://cernvm.cern.ch/config/')
        _config = response.read()

        # Parse response
        _params = {}
        _config = _config.split("\n")
        for line in _config:
            if line:
                (k, v) = line.split('=', 1)
                _params[k] = v

        # Generate JSON map for the CERNVM_REPOSITORY_MAP
        _cvmMap = {}
        _map = _params['CERNVM_REPOSITORY_MAP'].split(",")
        for m in _map:
            (name, _optlist) = m.split(":", 1)
            options = _optlist.split("+")
            _cvmMap[name] = options

        # Update CERNVM_REPOSITORY_MAP
        _params['CERNVM_REPOSITORY_MAP'] = json.dumps(_cvmMap)
        _params['CERNVM_ORGANISATION_LIST'] = _params[
            'CERNVM_ORGANISATION_LIST'].split(',')

        # Return parameters
        return _params

    except Exception as ex:
        print "Got error: %s\n" % str(ex)
        return {}


def _prompt_unencrypt_context(request, ctx, callback_url, decode_data=True,
                              decode_render=False):
    """
    Takes care of prompting user for a password and returning an unencrypted
    version of a given context "data" section and "rendered" representation.
    Decoded data is returned as strings. No "unpickling" is performed
    """
    resp = {}
    title = 'Context encrypted'
    body = 'The context information you are trying to use are encrypted with ' \
        'a private key. Please enter such key below to decrypt:'

    if 'password' in request.POST:
        # POST already contains 'unicode' data!
        pwd = request.POST['password'].encode('ascii', 'ignore')
        if salt_context_key(ctx.id, pwd) == ctx.key:
            # Password is OK: decrypt
            if decode_data:
                resp['data'] = crypt.decrypt(
                    base64.b64decode(str(ctx.data)), pwd)
            if decode_render:
                render = ContextStorage.objects.get(id=ctx.id)
                m = re.search(r"^ENCRYPTED:(.*)$", render.data)
                if m:
                    resp['render'] = crypt.decrypt(
                        base64.b64decode(str(m.group(1))), pwd)
                # Response empty in case of problems
        else:
            # Password is wrong
            resp['httpresp'] = render_password_prompt(
                request, title, body, callback_url,
                {'msg_error': 'Wrong password'}
            )
    else:
        # Prompt for password
        resp['httpresp'] = render_password_prompt(request, title, body,
                                                  callback_url)

    return resp


def _name_increment_revision(name):
    """
    If the given (context) name ends with a number, returns the same name with
    that number incremeted by one. In case it doesn't, appends a '(copy)' at the
    end of the given name.
    """
    revre = r'^(.*?)([0-9]+)$'
    m = re.search(revre, name)
    if m:
        name = m.group(1) + str(int(m.group(2)) + 1)
    else:
        name = name + ' (copy)'
    return name

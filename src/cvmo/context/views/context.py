import urllib2
import json
import pickle
import hashlib
import base64
import re
import copy

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
#from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q

from cvmo.context.plugins import ContextPlugins
from cvmo.context.models import ContextStorage, ContextDefinition
from cvmo.querystring_parser import parser

from cvmo.context.utils.views import uncache_response, render_error, render_confirm, render_password_prompt
from cvmo.context.utils.context import gen_context_key, salt_context_key
from cvmo.context.utils import crypt

from cvmo.context.utils.views import get_list_allowed_abstract

# String corresponding to the generic plugin name
global generic_plugin
generic_plugin = {
    'title': 'Basic CernVM configuration',
    'name': 'generic_cernvm',
    'display': True,
    'enabled': True
}

def get_cernvm_config():
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
        _params['CERNVM_ORGANISATION_LIST'] = _params['CERNVM_ORGANISATION_LIST'].split(',')

        # Return parameters
        return _params

    except Exception as ex:
        print "Got error: %s\n" % str(ex)
        return {
        }

def api_get(request, context_id, format, askpass):
    """ Returns the context definition in different formats and takes care of decrypting if requested """

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
            resp = prompt_unencrypt_context(request, ctx, '',
                decode_render=need_render)
            if 'httpresp' in resp:
                # Prompt
                return resp['httpresp']
            else:
                # Decrypt

                # When requested, data must be unpickled
                if need_data:
                    if not 'data' in resp:
                        return HttpResponse('db-error-data', content_type='text/plain')
                    else:
                        data = pickle.loads(resp['data'])

                # When requested, rendered part must be present
                if need_render:
                    if not 'render' in resp:
                        return HttpResponse('db-error-render', content_type='text/plain')
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
                return HttpResponse('not-found-rendered', content_type='text/plain')

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
            return HttpResponse('render-encoding-error', content_type='text/plain')

    # Return
    # if ctx.key:
    #     enc = 'yes'
    # else:
    #     enc = 'no'
    #return HttpResponse('format:'+format+';encrypted:'+enc+';data:'+output, content_type='text/plain')
    return HttpResponse(output, content_type='text/plain')

# Changes the published value of a given context. Obtains all the parameters
# (id and action) through HTTP GET. Returns a HTTP status != 200 in case of
# errors, or an HTTP 200 with a JSON file containing the string '1' when OK
def ajax_publish_context(request):
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
        Q(id=id) & Q(inherited=False) & Q(owner=request.user) );
    if not ctx.exists or ctx.update(public=publish) != 1:
        return render_error(request, 500, 'Update error')

    # Will return the string '1' in case of success, '0' in case of failure
    return uncache_response(HttpResponse('1', content_type="application/json"))

# Gets the list of abstract contexts with the following fields:
#   id, name, public
# Users will get a list of the "shown" ones only plus their own. If
# is_abstract_creation_enabled == True, the full list is obtained.
def ajax_abstract_list(request):
    ab_list = get_list_allowed_abstract(request)
    ab_dict = []
    for ab in ab_list:
        ab_dict.append({
            'id': ab.id,
            'name': ab.name,
            'public': ab.public
        })
    return uncache_response(HttpResponse(
        json.dumps(ab_dict, indent=2), content_type="application/json"))

def ajax_list(request):

    # Require 'query'
    if not 'query' in request.GET:
        return render_error(request, 400)

    # Fetch query
    query = request.GET['query']

    # Query database
    _ans = []
    resultset = ContextDefinition.objects.filter(Q(name__contains=query), Q(public=True) | Q(owner=request.user), Q(inherited=False))[:10]
    for c in resultset:

        # Check for key and add the image suffix
        suffix = ''
        if c.key != '':
            suffix = '_key'

        # Define the icon
        icon = '<img src="/static/images/user' + suffix + '.png" style="width:14px;height:14px" align="baseline" /> '
        if (c.public):
            icon = '<img src="/static/images/public' + suffix + '.png" style="width:14px;height:14px" align="baseline" /> '

        # Define if the
        has_key = False
        if c.key != "":
            has_key = True

        # Push the result
        _ans.append(
            {
                'label':c.name,
                'text':icon + c.name + '<br /><small>Author: <em>'
                    + c.owner.first_name + ' ' + c.owner.last_name + '</em><br />Description: <em>'
                    + c.description + '</em></small>',
                'attributes': {
                   "has_key": has_key,
                   "uid": c.id
                }
            }
        )

    # Return response
    return uncache_response(HttpResponse(json.dumps(_ans), content_type="application/json"))

def blank_abstract(request):

    p_names = ContextPlugins().get_names()
    p_dict = []

    p_dict.append(generic_plugin)

    # A default html_body value for convenience
    abstract = {
        'html_body': """
<table class="plain long-text">
    <tr>
        <th width="150">Multiple choices:</th>
        <td>
            <select name="values[custom][multiple]">
                <option value="choice#1">1st choice</option>
                <option value="choice#2">2nd choice</option>
            </select>
        </td>
    </tr>
    <tr>
        <th width="150">Input text:</th>
        <td><input name="values[custom][text]" value="any text value"/></td>
    </tr>
</table>
"""
    }

    for p_n in p_names:
        p = ContextPlugins().get(p_n)
        p_dict.append({'title': p.TITLE, 'name': p_n})

    # Render the response
    return render_to_response('pages/abstract.html', {
        'plugins': p_dict,
        'abstract': abstract
    }, RequestContext(request))

def create_abstract(request):
    post_dict = parser.parse(request.POST.urlencode())

    # We are interested in values, enabled and abstract. Let's insert empty
    # values in case some of them are null (values and abstract are never null)
    if post_dict.get('enabled') == None:
        post_dict['enabled'] = {}

    # There is no specific model for the abstract context, so we will just use
    # the ContextDefinition model. Since this context is abstract, no rendered
    # version will be saved in ContextStorage
    c_uuid = gen_context_key()
    c_data = pickle.dumps({
        'values'   : post_dict['values'],
        'enabled'  : post_dict['enabled'],
        'abstract' : post_dict['abstract']
    })

    # For debug
    # return uncache_response(HttpResponse(json.dumps(post_dict, indent=2), \
    #     content_type="text/plain"))

    e_context = ContextDefinition.objects.create(
        id=c_uuid,
        name=str( post_dict['values']['name'] ),
        description='',  # TODO
        owner=request.user,
        key='',
        public=False,  # TODO
        data=c_data,
        checksum=0,  # TODO
        inherited=False,
        abstract=True
    )

    return redirect('dashboard')

def blank(request):
    # Empty values
    values = { }

    # Render all of the plugins
    plugins = ContextPlugins().renderAll(request, values)

    # Append display property to every plugin, and set it to True
    for p in plugins:
        p['display'] = True

    # Render the response
    return render_to_response('pages/context.html', {
        'cernvm': get_cernvm_config(),
        'values': values,
        'disabled': False,
        'id': '',
        'plugins': plugins,
        'cernvm_plugin': generic_plugin
    }, RequestContext(request))

def create(request):
    post_dict = parser.parse( unicode(request.POST.urlencode()).encode('utf-8') )

    # The values of all the plugins and the enabled plugins
    values = post_dict.get('values')
    enabled = post_dict.get('enabled')
    abstract = post_dict.get('abstract')

    # Generate a UUID for this context
    c_uuid = gen_context_key()

    # Collect data to save. Non-indexed data is pickled
    raw_values = { 'values': values, 'enabled': enabled }
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
        c_config = "ENCRYPTED:" + base64.b64encode(crypt.encrypt(c_config, c_key))
        c_key = salt_context_key(c_uuid, c_key)

    # Check if this is public
    c_public = False
    if ('public' in values) and (values['public']):
        c_public = True

    # For debug
    # return uncache_response(
    #     HttpResponse(json.dumps(raw_values, indent=2), content_type="text/plain")
    # )

    # Save context definition
    e_context = ContextDefinition.objects.create(
            id=c_uuid,
            name=str(values['name']),
            description=str(values['description']),
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
    e_data = ContextStorage.objects.create(
            id=c_uuid,
            data=c_config
        )

    # Go to dashboard
    return redirect('dashboard')

# Takes care of prompting user for a password and returning an unencrypted
# version of a given context "data" section and "rendered" representation.
# Decoded data is returned as strings. No "unpickling" is performed
def prompt_unencrypt_context(request, ctx, callback_url, decode_data=True, decode_render=False):
    resp = {}
    title = 'Context encrypted'
    body = 'The context information you are trying to use are encrypted with ' \
        'a private key. Please enter such key below to decrypt:'

    if 'password' in request.POST:
        # POST already contains 'unicode' data!
        #pwd = request.POST['password'].decode('utf-8', 'ignore').encode('ascii', 'ignore')
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
            resp['httpresp'] = render_password_prompt(request, title, body,
                callback_url, { 'msg_error': 'Wrong password' });
    else:
        # Prompt for password
        resp['httpresp'] = render_password_prompt(request, title, body,
            callback_url);

    return resp

def clone(request, context_id):

    # Fetch the entry from the db
    item = ContextDefinition.objects.get(id=context_id)
    data = {}

    # Check if the data are encrypted
    if item.key == '':
        data = pickle.loads(str(item.data))
    else:
        # Password-protected
        resp = prompt_unencrypt_context(request, item,
            reverse('context_clone', kwargs={'context_id': context_id}))
        if 'httpresp' in resp:
            return resp['httpresp']
        elif 'data' in resp:
            data = pickle.loads(resp['data'])

    # Render all of the plugins
    plugins = ContextPlugins().renderAll(request, data['values'], data['enabled'])

    # Append display property to every plugin, and set it to True
    for p in plugins:
        p['display'] = True

    data['values']['name'] = name_increment_revision(data['values']['name'])

    # Render the response
    #raw = {'data':data}  # debug
    return render_to_response('pages/context.html', {
        'cernvm': get_cernvm_config(),
        'values': data['values'],
        'id': context_id,
        'disabled': False,
        #'raw': json.dumps(raw, indent=2),
        'plugins': plugins,
        'cernvm_plugin': generic_plugin
    }, RequestContext(request))

def clone_abstract(request, context_id):
    item = ContextDefinition.objects.get(id=context_id)
    data = pickle.loads(str(item.data))
    display = data['abstract'].get('display')

    p_names = ContextPlugins().get_names()
    p_dict = []

    # Display CernVM generic plugin? (It is always enabled anyway)
    generic_plugin_cp = copy.deepcopy(generic_plugin)
    if display == None:
        generic_plugin_cp['display'] = False
    else:
        generic_plugin_cp['display'] = \
          ( display.get(generic_plugin['name']) == 1 )

    p_dict.append(generic_plugin_cp)

    for p_n in p_names:
        p = ContextPlugins().get(p_n)
        p_e = ( data['enabled'].get(p_n) == 1 )
        if display != None:
            p_d = ( display.get(p_n) == 1 )
        else:
            p_d = False
        p_dict.append({'title': p.TITLE, 'name': p_n,
            'enabled': p_e, 'display': p_d})

    data['values']['name'] = name_increment_revision(data['values']['name'])

    return render_to_response('pages/abstract.html', {
        'values': data['values'],
        'abstract': data['abstract'],
        'enabled': data['enabled'],
        'plugins': p_dict
    }, RequestContext(request))

# If the given (context) name ends with a number, returns the same name with
# that number incremeted by one. In case it doesn't, appends a '(copy)' at the
# end of the given name.
def name_increment_revision(name):
    revre = r'^(.*?)([0-9]+)$'
    m = re.search(revre, name)
    if m:
        name = m.group(1) + str(int(m.group(2))+1)
    else:
        name = name + ' (copy)'
    return name

# Used both when creating a simple context and when cloning it
def context_from_abstract(request, context_id, cloning=False):
    item = ContextDefinition.objects.get(id=context_id)

    # Check if the data are encrypted
    if item.key == '':
        data = pickle.loads(str(item.data))
    else:
        # Password-protected
        resp = prompt_unencrypt_context(request, item,
            reverse('context_clone_simple', kwargs={'context_id': context_id}))
        if 'httpresp' in resp:
            return resp['httpresp']
        elif 'data' in resp:
            data = pickle.loads(resp['data'])

    display = data['abstract'].get('display')

    # Render all of the plugins
    plugins = ContextPlugins().renderAll(request, data['values'],
        data['enabled'])

    # Append display property to every plugin. Defaults to False
    for p in plugins:
        if display == None:
            p['display'] = False  # default
        else:
            p['display'] = ( display.get(p['id']) == 1 )

    # Display CernVM generic plugin? (It is always enabled anyway)
    generic_plugin_cp = copy.deepcopy(generic_plugin)
    if display == None:
        generic_plugin_cp['display'] = False
    else:
        generic_plugin_cp['display'] = ( display.get(generic_plugin['name']) == 1 )

    # Change original name
    if cloning:
        data['values']['name'] = name_increment_revision(data['values']['name'])
    else:
        data['values']['name'] = 'Context from ' + data['values']['name']

    # Render the response
    #raw = {'data': data}  # debug
    return render_to_response('pages/context.html', {
        'cernvm': get_cernvm_config(),
        'values': data['values'],
        'json_values': json.dumps(data['values']),
        'disabled': False,
        'id': '',
        'parent_id': context_id,
        #'raw': json.dumps(raw, indent=2),
        'abstract_html': data['abstract'].get('html_body'),
        'from_abstract': True,
        'plugins': plugins,  # now each plugin will hold enable=True|False
        'cernvm_plugin': generic_plugin_cp
    }, RequestContext(request))

def view(request, context_id):

    # Fetch the entry from the db
    item = ContextDefinition.objects.get(id=context_id)
    data = {}

    # Check if the data are encrypted
    if item.key == '':
        data = pickle.loads(str(item.data))
    else:
        # Password-protected
        resp = prompt_unencrypt_context(request, item,
            reverse('context_view', kwargs={'context_id': context_id}))
        if 'httpresp' in resp:
            return resp['httpresp']
        elif 'data' in resp:
            data = pickle.loads(resp['data'])

    # Render all of the plugins
    plugins = ContextPlugins().renderAll(request, data['values'], data['enabled'])

    # Append display property to every plugin, and set it to True
    for p in plugins:
        p['display'] = True

    # Render the response
    return render_to_response('pages/context.html', {
        'cernvm': get_cernvm_config(),
        'values': data['values'],
        'id': context_id,
        'disabled': True,
        'plugins': plugins,
        'cernvm_plugin': generic_plugin
    }, RequestContext(request))

def delete(request, context_id):
    # Try to find the context
    try:
        context = ContextDefinition.objects.get(id=context_id)
    except:
        request.session["redirect_msg_error"] = "Context with id " + context_id + " does not exist!"
        return redirect("dashboard")

    # Check if context belongs to calling user
    if request.user.id != context.owner.id:
        request.session["redirect_msg_error"] = "Context with id " + context_id + " does not belong to you!"
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
        return render_confirm(request, 'Delete context',
                              'Are you sure you want to delete this contextualization information? This action is not undoable!',
                              reverse('context_delete', kwargs={'context_id':context_id}) + '?confirm=yes',
                              reverse('dashboard')
                              )

import urllib2
import json
import pickle
import uuid
import hashlib
import base64

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
from cvmo.context.utils import crypt

def gen_context_key():
    return uuid.uuid4().hex

def get_cernvm_config():
    """ Download the latest configuration parameters from CernVM """
    response = urllib2.urlopen('http://cernvm.cern.ch/config/')
    _config = response.read()
    
    # Parse response
    _params = {}
    _config = _config.split("\n")
    for line in _config:
        if line:
            (k, v) = line.split('=',1)
            _params[k]=v
    
    
    # Generate JSON map for the CERNVM_REPOSITORY_MAP
    _cvmMap = {}
    _map = _params['CERNVM_REPOSITORY_MAP'].split(",")
    for m in _map:
        (name, _optlist) = m.split(":",1)
        options = _optlist.split("+")
        _cvmMap[name] = options
    
    # Update CERNVM_REPOSITORY_MAP
    _params['CERNVM_REPOSITORY_MAP'] = json.dumps(_cvmMap)
    _params['CERNVM_ORGANISATION_LIST'] = _params['CERNVM_ORGANISATION_LIST'].split(',')
    
    # Return parameters
    return _params
    
def api_get(request, context_id):
    """ Return the context definition in text format """
    
    # Fetch the specified context
    try:
        context = ContextStorage.objects.get(id=context_id)
        return HttpResponse(context.data, content_type="text/plain")
        
    except:
        return HttpResponse("not-found", content_type="text/plain")

def ajax_list(request):
    
    # Require 'query'
    if not 'query' in request.GET:
        return render_error(request, 400)

    # Fetch query
    query = request.GET['query']

    # Query database
    _ans = []
    resultset = ContextDefinition.objects.filter(Q(name__contains=query), Q(public=True) | Q(owner=request.user))[:10]
    for c in resultset:
        
        # Check for key and add the image suffix
        suffix=''
        if c.key != '':
            suffix='_key'
        
        # Define the icon
        icon='<img src="/static/images/user'+suffix+'.png" style="width:14px;height:14px" align="baseline" /> '
        if (c.public):
            icon = '<img src="/static/images/public'+suffix+'.png" style="width:14px;height:14px" align="baseline" /> '
        
        # Push the result
        _ans.append({ 'label':c.name, 'text':icon+c.name+'<br /><small>Author: <em>'+c.owner.first_name+' '+c.owner.last_name+'</em><br />Description: <em>'+c.description+'</em></small>' })

    # Return response
    return uncache_response(HttpResponse(json.dumps(_ans), content_type="application/json"))

def blank(request):
    # Empty values
    values = { }
    
    # Render all of the plugins
    plugins = ContextPlugins().renderAll(request, values)

    # Render the response
    return render_to_response('pages/context.html', {
        'cernvm': get_cernvm_config(),
        'values': values,
        'disabled': False,
        'id': '',
        'plugins': plugins
    }, RequestContext(request))

def create(request):
    post_dict = parser.parse(request.POST.urlencode())
    
    # The values of all the plugins and the enabled plugins
    values = post_dict.get('values')
    enabled = post_dict.get('enabled')
    
    # Prepare pickled data for easy reconstruction
    # (in case somebody wants to clone a template)
    c_values = pickle.dumps({'values':values, 'enabled':enabled})
    c_config = ContextPlugins().renderContext(values, enabled)
    
    # Generate checksum of the configuration 
    c_checksum = hashlib.sha1(c_config).hexdigest()
    
    # Generate a UUID for this context
    c_uuid = gen_context_key()
    
    # Get the possible secret key
    c_key = ""
    if ('protect' in values) and (values['protect']):
        c_key = values['secret']
    
    # If the content is encrypted process the data now
    if (c_key != ''):
        c_values = base64.b64encode(crypt.encrypt(c_values, c_key))
        c_config = "ENCRYPTED:"+base64.b64encode(crypt.encrypt(c_config, c_key))
        c_key = hashlib.sha1(c_uuid+':'+c_key).hexdigest()
    
    # Check if this is public
    c_public = False
    if ('public' in values) and (values['public']):
        c_public = True
    
    # Save context definition
    e_context = ContextDefinition.objects.create(
            id = c_uuid,
            name = values['name'],
            description = values['description'],
            owner = request.user,
            key = c_key,
            public = c_public,
            data = c_values,
            checksum = c_checksum
        )
    
    # Save context data (Should go to key/value store for speed-up)
    e_data = ContextStorage.objects.create(
            id = c_uuid,
            data = c_config
        )
    
    # Go to dashboard
    return redirect('dashboard')

def clone(request, context_id):
    
    # Fetch the entry from the db
    item = ContextDefinition.objects.get(id=context_id)
    data = {}
    
    # Check if the data are encrypted
    if item.key == '':
        data = pickle.loads( str(item.data) )
        
    else:
        
        # Fetch the key from the POST variables
        if 'password' in request.POST:
            
            # Validate password
            try:
                if hashlib.sha1(context_id+':'+request.POST['password']).hexdigest() != item.key:
                    return render_password_prompt(request, 'Context encrypted', 
                        'The context information you are trying to use are encrypted with a private key. Please enter this key below to decrypt them:',
                        reverse('context_clone', kwargs={'context_id':context_id}),
                        { 'msg_error': 'Password mismatch' }
                        )
            except Exception as ex:
                return render_password_prompt(request, 'Context encrypted', 
                    'The context information you are trying to use are encrypted with a private key. Please enter this key below to decrypt them:',
                    reverse('context_clone', kwargs={'context_id':context_id}),
                    { 'msg_error': 'Decryption error: %s' % str(ex) }
                    )
                
            # Decode data
            data = pickle.loads( crypt.decrypt( base64.b64decode(str(item.data)), request.POST['password'].decode("utf-8").encode('ascii','ignore') ) )
            
        else:
            # Key does not exist in session? 
            return render_password_prompt(request, 'Context encrypted', 
                'The context information you are trying to use are encrypted with a private key. Please enter this key below to decrypt them:',
                reverse('context_clone', kwargs={'context_id':context_id})
                )
    
    # Render all of the plugins
    plugins = ContextPlugins().renderAll(request, data['values'], data['enabled'])

    # Render the response
    return render_to_response('pages/context.html', {
        'cernvm': get_cernvm_config(),
        'values': data['values'],
        'id': context_id,
        'disabled': False,
        'plugins': plugins
    }, RequestContext(request))
    
def view(request, context_id):
    
    # Fetch the entry from the db
    item = ContextDefinition.objects.get(id=context_id)
    data = {}
    
    # Check if the data are encrypted
    if item.key == '':
        data = pickle.loads( str(item.data) )
        
    else:
        
        # Fetch the key from the POST variables
        if 'password' in request.POST:
            
            # Validate password
            try:
                if hashlib.sha1(context_id+':'+request.POST['password']).hexdigest() != item.key:
                    return render_password_prompt(request, 'Context encrypted', 
                        'The context information you are trying to use are encrypted with a private key. Please enter this key below to decrypt them:',
                        reverse('context_view', kwargs={'context_id':context_id}),
                        { 'msg_error': 'Password mismatch' }
                        )
            except Exception as ex:
                return render_password_prompt(request, 'Context encrypted', 
                    'The context information you are trying to use are encrypted with a private key. Please enter this key below to decrypt them:',
                    reverse('context_view', kwargs={'context_id':context_id}),
                    { 'msg_error': 'Decryption error: %s' % str(ex) }
                    )
                
            # Decode data
            data = pickle.loads( crypt.decrypt( base64.b64decode(str(item.data)), request.POST['password'].decode("utf-8").encode('ascii','ignore') ) )
            
        else:
            # Key does not exist in session? 
            return render_password_prompt(request, 'Context encrypted', 
                'The context information you are trying to use are encrypted with a private key. Please enter this key below to decrypt them:',
                reverse('context_view', kwargs={'context_id':context_id})
                )
        
    
    # Render all of the plugins
    plugins = ContextPlugins().renderAll(request, data['values'], data['enabled'])

    # Render the response
    return render_to_response('pages/context.html', {
        'cernvm': get_cernvm_config(),
        'values': data['values'],
        'id': context_id,
        'disabled': True,
        'plugins': plugins
    }, RequestContext(request))

def delete(request, context_id):
    # Is it confirmed?
    if ('confirm' in request.GET) and (request.GET['confirm'] == 'yes'):
        # Delete the specified contextualization entry
        ContextDefinition.objects.filter(id=context_id).delete()
        ContextStorage.objects.filter(id=context_id).delete()
        
        # Go to dashboard
        return redirect('dashboard')
        
    else:
        # Show the confirmation screen
        return render_confirm(request, 'Delete context', 
                              'Are you sure you want to delete this contextualization information? This action is not undoable!',
                              reverse('context_delete', kwargs={'context_id':context_id})+'?confirm=yes',
                              reverse('dashboard')
                              )

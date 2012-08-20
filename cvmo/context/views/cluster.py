import pickle
import hashlib

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from cvmo.context.plugins import ContextPlugins
from cvmo.context.models import ClusterDefinition, ContextDefinition, \
    ContextStorage, ClusterInstance
from cvmo.querystring_parser import parser

from cvmo.context.utils.context import gen_context_key, salt_context_key
from cvmo.context.utils.views import uncache_response, render_confirm
from django.core.urlresolvers import reverse
from cvmo.context.utils import crypt
import base64
import pprint
from django.db.models.query_utils import Q

"""
    Django template engine does not support the dictionary lookup
    using a variable as a key. Therefore service_offerings is a list of
    hashes instead of a dictionary (which would make much more sense)...
"""
service_offerings = [
    { "value": "small", "label": "Small" },
    { "value": "medium", "label": "Medium" },
    { "value": "large", "label": "Large" },
    { "value": "xlarge", "label": "Extra large" }
]

cernvm_versions = [
    { "value": "", "label": "Any" },
    { "value": "2.5.3", "label": "2.5.3" },
    { "value": "2.5.1", "label": "2.5.1" },
    { "value": "2.4.0", "label": "2.4.0" },
    { "value": "2.3.0", "label": "2.3.0" },
    { "value": "2.2.0", "label": "2.2.0" },
    { "value": "2.1.0", "label": "2.1.0" },
    { "value": "2.0.7", "label": "2.0.7" },
    { "value": "2.0.5", "label": "2.0.5" }                   
]

def api_get_definition(request, cluster_id):
    # Is cluster id defined?
    if cluster_id == "":
        return uncache_response(HttpResponse("not-found", content_type="text/plain"))
    
    # Is authenticated?
    authenticated = False
    
    # Fetch the specified cluster
    try:
        cluster = ClusterDefinition.objects.get(id=cluster_id)
    except:
        return uncache_response(HttpResponse("not-found", content_type="text/plain"))
        
    # Create response
    response = {
        "name": cluster.name,
        "description": cluster.description,
        "owner": cluster.owner.username,
        "has_agent": cluster.agent,
        "public": cluster.public,
        "instances": []
    }
    
    # Translate the data of the cluster
    cluster_data = pickle.loads(cluster.data)
    
    # Iterate through the instances to fill response
    for instance in cluster_data["instances"]:
        response_instance = {
            "from_amt": instance["from_amt"],
            "to_amt": instance["to_amt"],
            "elastic": instance["elastic"],
            "contextid": instance["contextid"],
            "context_name": instance["context_name"]
        }
        if authenticated:
            response_instance["data"] = instance["data"]
        response["instances"].append(response_instance)
        
    # Serialize the response
    response_str = pickle.dumps(response)
    
    return uncache_response(HttpResponse(response_str, content_type="text/plain"))        
    
    
def blank(request):
    return render_to_response('pages/cluster.html', {
        "values": {
            "instances": []
        },
         "service_offerings": service_offerings,
         "cernvm_versions": cernvm_versions,
        "disabled": False
    }, RequestContext(request))

def context_get_key(name):
    ctx = ContextDefinition.objects.get(name=name)
    return ctx.key

def create(request):
    post_dict = parser.parse(request.POST.urlencode())
    
    # The values of all the plugins and the enabled plugins
    values = post_dict.get('values')
    enabled = post_dict.get('enabled')
    
    # Generate a UUID for this context
    c_uuid = gen_context_key()
    
    # There is a key?
    c_key = ""
    if ('protect' in values) and (values['protect']):
        c_key = str(values['secret'])
        
    # Check if this is public
    c_public = False
    if ('public' in values) and (values['public']):
        c_public = True
        
    # Check if it has agent enabled
    c_agent = False
    if "agent" in values and values["agent"]:
        c_agent = True
        
    # Get serialized context data
    c_data = pickle.dumps({ "values": values, "enabled": enabled })
    
    # Encrypt data?
    if c_key != "":
        c_data = base64.b64encode(crypt.encrypt(c_data, c_key))
        
    # Save context definition
    cluster = ClusterDefinition.objects.create(
        id=c_uuid,
        name=str(values['name']),
        description=str(values['description']),
        cernvm_version = str(values["cernvm_version"]),
        owner=request.user,
        key="",
        public=c_public,
        agent=c_agent,
        data=c_data
    )      
        
    # Get instances
    i = 0
    for index in values["instances"]:
        instance = values["instances"][index]
        
        # Get the context definition
        try:
            context = ContextDefinition.objects.get(name=str(instance["context"]))
        except Exception:
            # Context not found for this instance
            cluster.delete()
            return render_to_response('pages/cluster.html', {
                "values" : post_dict['values'],
                "service_offerings": service_offerings,
                "cernvm_versions": cernvm_versions,
                "disabled": False,
                "msg_info": "",
                "msg_warning": instance["context"] + " context was not found!"
            }, RequestContext(request))
            
        # Get old key
        if "key" not in instance:
            old_key = ""
        else:
            old_key = str(instance["key"])
        
        # Check if it has a key
        if context.key is not None \
            and context.key != "":
            # User should had define the key of the context
            if old_key == "":
                cluster.delete()
                return render_to_response('pages/cluster.html', {
                    "values" : post_dict['values'],
                    "service_offerings": service_offerings,
                    "cernvm_versions": cernvm_versions,
                    "disabled": False,
                    "msg_info": "",
                    "msg_warning": str(instance["context"]) + " context is encrypted. Please provide the key!"
                }, RequestContext(request))                        
                
            # Check that key is correct
            if context.key != salt_context_key(context.id, old_key):
                cluster.delete()
                return render_to_response('pages/cluster.html', {
                    "values" : post_dict['values'],
                    "service_offerings": service_offerings,
                    "cernvm_versions": cernvm_versions,
                    "disabled": False,
                    "msg_info": "",
                    "msg_warning": str(instance["context"]) + " context key is invalid!"
                }, RequestContext(request))
                            
            # User had defined the correct key, get data by decrypting
            decryption_key = old_key.decode("utf-8").encode("ascii", "ignore")
            unencrypted_data = crypt.decrypt(base64.b64decode(context.data), decryption_key)            
            data = pickle.loads(unencrypted_data)
        else:        
            # Get the data
            data = pickle.loads(context.data)

        # Set the agent
        if c_agent:
            data["values"]["agent"] = True
            
        # Add the environment variables
        if "environment" in values:
            if "environment" not in data["values"]["general"]:
                data["values"]["general"]["environment"] = {}
            for var in values["environment"]:
                data["values"]["general"]["environment"][str(var)] = str(values["environment"][var])
            
        # Create new cluster declaration
        cont_uuid = gen_context_key()
        cont_key = c_key
        cont_values = pickle.dumps(data)
        cont_config = ContextPlugins().renderContext(cont_uuid, data["values"], data["enabled"])
        # Generate checksum of the configuration 
        cont_checksum = hashlib.sha1(cont_config).hexdigest()            
        
        # If the content is encrypted process the data now
        if cont_key != '':
            cont_values = base64.b64encode(crypt.encrypt(cont_values, cont_key))
            cont_config = "ENCRYPTED:" + base64.b64encode(crypt.encrypt(cont_config, cont_key))
            cont_key = salt_context_key(cont_uuid, cont_key)
            
        # Save context definition
        e_context = ContextDefinition.objects.create(
            id=cont_uuid,
            name=cluster.name + ": " + context.name,
            description=context.description,
            owner=request.user,
            key=cont_key,
            public=False,
            data=cont_values,
            checksum=cont_checksum,
            inherited=True
        )
        
        # Save context data (Should go to key/value store for speed-up)
        ContextStorage.objects.create(
            id=cont_uuid,
            data=cont_config
        )       
        
        # Get elastic value
        cont_elastic = False
        if "elastic" in instance and instance["elastic"]:
            cont_elastic = True
        
        # Save instance
        ClusterInstance.objects.create(
            cluster=cluster,
#            order=instance["order"],
            order=i,
            context=e_context,
            from_amt=instance["from_amt"],
            to_amt=instance["to_amt"],
            elastic=cont_elastic,
            service_offering=str(instance["service_offering"])
        )             
        i += 1
        
    if c_key != "":
        # Store key, hashed
        c_key = salt_context_key(c_uuid, c_key)
        cluster.key = c_key
        cluster.save()                
    
    # Go to dash board
    return redirect('dashboard')
        
def clone(request, cluster_id):
    pass

def view(request, cluster_id):
    pass

def delete(request, cluster_id):
    # Get the cluster
    try:
        cluster = ClusterDefinition.objects.get(id=cluster_id)
    except:
        # Go to dashboard
        request.session["redirect_msg_error"] = "Requested cluster id not found!"
        return redirect('dashboard')
    
    # Check the user
    if cluster.owner != request.user:
        # Go to dashboard
        request.session["redirect_msg_error"] = "You are not authorized to remove the cluster."
        return redirect('dashboard')
    
    # Is it confirmed?
    if ('confirm' in request.GET) and (request.GET['confirm'] == 'yes'):        
        # Delete the specified cluster definition
        cluster.delete()
        
        # Redirect to dashboard
        request.session["redirect_msg_success"] = "Cluster " + cluster_id + " was removed successfully!"
        return redirect( 'dashboard' )
    else:
        # Show the confirmation screen
        return render_confirm(
            request, 'Delete cluster',
            'Are you sure you want to delete this cluster definition? This action is not undoable!',
            reverse('cluster_delete', kwargs={'cluster_id':cluster_id}) + '?confirm=yes',
            reverse('dashboard')
        )

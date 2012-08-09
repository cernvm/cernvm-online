import pickle
import hashlib

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from cvmo.context.plugins import ContextPlugins
from cvmo.context.models import ClusterDefinition, ContextDefinition
from cvmo.querystring_parser import parser

from cvmo.context.utils.context import gen_context_key
from cvmo.context.utils.views import uncache_response, render_confirm
from django.core.urlresolvers import reverse

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
        
    # Create the instances structure
    c_instances = []
    
    # Get instances
    for index in values["instances"]:
        instance = values["instances"][index]
        
        # Get the context definition
        try:
            context = ContextDefinition.objects.get(name=instance["context"])
        except Exception:
            # Context not found for this instance
            return render_to_response('pages/cluster.html', {
                "values" : post_dict['values'],
                "disabled": False,
                "msg_info": "",
                "msg_warning": instance["context"] + " context was not found!"
            }, RequestContext(request))
        
        # Get the data
        data = pickle.loads(context.data)

        # Set the agent
        if c_agent:
            data["values"]["agent"] = False
            
        # Add the environment variables
        if "environment" not in data["values"]["general"]:
            data["values"]["general"]["environment"] = {}
        for var in values["environment"]:
            data["values"]["general"]["environment"][var] = values["environment"][var]
            
        # Create cluster_instance object
        cluster_instance = {
            "from_amt": instance["from_amt"],
            "to_amt": instance["to_amt"],
            "elastic": False,
            "contextid": context.id,
            "context_name": context.name
        }               
        if "elastic" in instance and instance["elastic"]:
            cluster_instance["elastic"] = True
            
        # Get Context AMI
        cluster_instance["data"] = ContextPlugins().renderContext(context.id, data["values"], data["enabled"])        
        # Create new checksum
        cluster_instance["checksum"] = hashlib.sha1(cluster_instance["data"]).hexdigest()
        
        c_instances.append(cluster_instance)
        
    # Get serialized context data
    c_data = pickle.dumps({ "values": values, "enabled": enabled, "instances": c_instances })
        
    # Save context definition
    ClusterDefinition.objects.create(
        id=c_uuid,
        name=values['name'],
        description=values['description'],
        owner=request.user,
        key=c_key,
        public=c_public,
        agent=c_agent,
        data=c_data
    )  
    
    # Go to dashboard
    return redirect('dashboard')
        
def clone(request, cluster_id):
    pass

def view(request, cluster_id):
    pass

def delete(request, cluster_id):
    # Is it confirmed?
    if ('confirm' in request.GET) and (request.GET['confirm'] == 'yes'):
        # Delete the specified cluster definiton
        ClusterDefinition.objects.filter(id=cluster_id).delete()        
        # Go to dashboard
        return redirect('dashboard')        
    else:
        # Show the confirmation screen
        return render_confirm(
            request, 'Delete cluster',
            'Are you sure you want to delete this cluster definition? This action is not undoable!',
            reverse('cluster_delete', kwargs={'cluster_id':cluster_id}) + '?confirm=yes',
            reverse('dashboard')
        )

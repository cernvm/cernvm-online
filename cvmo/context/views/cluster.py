from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from cvmo.context.models import ServiceOffering, DiskOffering, NetworkOffering, \
    Template, ServiceDefinition, ClusterDefinition, ContextStorage, \
    ContextDefinition
from cvmo.context.utils.views import msg_info, msg_error
from cvmo.querystring_parser import parser
import re
from cvmo.context.utils.context import salt_context_key, gen_context_key
import base64
from cvmo.context.utils import crypt
from cvmo.context.utils.views import render_confirm, uncache_response, for_cloud
from django.core.urlresolvers import reverse
from types import StringType
from django.http import HttpResponse
import json
import hashlib
import pprint
import uuid

##################################################
# Request handlers
##################################################

@for_cloud
def create( request ):
    """
    Cluster create view
    """
    
    # Setup values
    context = _getCreateViewContext()
    context['disabled'] = False
    context['values'] = _emptyValues()
    
    # Send response
    return render_to_response( "pages/cluster.html", 
       context, 
       RequestContext( request ) )

@for_cloud
def do_create( request ):
    """
    Submit the creation of a cluster
    """
    post_dict = parser.parse( request.POST.urlencode() )
    if post_dict:
    
        # Create cluster with the values given
        _createClusterDefinition(request, post_dict['values'])
        
        # Go to dashboard
        return redirect('dashboard')
    
    else:
        
        # Invalid request? Go back to create cluster
        return redirect("cluster_create")

@for_cloud
def clone( request, cluster_id ):
    """
    Create a clone of the given cluster id
    """
    
    # Fetch record
    i_cluster = ClusterDefinition.objects.get(id=cluster_id, owner=request.user)
    if not i_cluster:
        msg_error(request, "The specified cluster ID was not found or you are not the owner!")
        return redirect('dashboard')
    
    i_services = ServiceDefinition.objects.filter(cluster=i_cluster)
    
    # Convert values
    values = {
        "name": i_cluster.name,
        "description": i_cluster.description,
        "services": _servicesToView( i_services )
    }
    
    print(str(values))
    
    # Setup values
    context = _getCreateViewContext()
    context['disabled'] = False
    context['values'] = values
    
    # Send response
    return render_to_response( "pages/cluster.html", 
       context, 
       RequestContext( request ) )


@for_cloud
def view( request, cluster_id ):
   """
   Create a clone of the given cluster id
   """

   # Fetch record
   i_cluster = ClusterDefinition.objects.get(id=cluster_id, owner=request.user)
   if not i_cluster:
       msg_error(request, "The specified cluster ID was not found or you are not the owner!")
       return redirect('dashboard')

   i_services = ServiceDefinition.objects.filter(cluster=i_cluster)

   # Convert values
   values = {
       "name": i_cluster.name,
       "description": i_cluster.description,
       "services": _servicesToView( i_services )
   }

   print(str(values))

   # Setup values
   context = _getCreateViewContext()
   context['disabled'] = True
   context['values'] = values

   # Send response
   return render_to_response( "pages/cluster.html", 
      context, 
      RequestContext( request ) )

@for_cloud
def delete( request, cluster_id ):
    # Try to find the cluster
    try:
        cluster = ClusterDefinition.objects.get( id = cluster_id )
    except:
        msg_error( "Cluster with id " + cluster_id + " does not exist!" )
        return redirect( "dashboard" )

    # Check if cluster belongs to calling user
    if request.user.id is not cluster.owner.id:
        msg_error( "Cluster with id " + cluster_id + " does not belong to you!" )
        return redirect( "dashboard" )

    # Is it confirmed?
    if ( "confirm" in request.GET ) \
        and ( request.GET['confirm'] == 'yes' ):
        # Delete services
        services = ServiceDefinition.objects.filter( cluster = cluster )
        for service in services:
            service.delete()

        # Delete the specified cluster entry
        cluster.delete()

        # Go to dashboard
        msg_info( request, "Cluster removed successfully!" )
        return redirect('dashboard')        
    else:
        # Show the confirmation screen
        return render_confirm( request, "Delete cluster", \
            "Are you sure you want to delete this cluster and it's services? This action is not undoable!", \
            reverse( 'cluster_delete', kwargs = { 'cluster_id': cluster_id } ) + '?confirm=yes', \
            reverse( 'dashboard' ) )


@for_cloud
def api_cloudinfo(request):
    
    # Build response
    response = { }
    
    try:
        # Fetch cloud information for this user
        lst_clusters = ClusterDefinition.objects.filter(owner=request.user)
        
        ans_clusters = []
        for cluster in lst_clusters:
            ans_services = []
            
            # Build services
            lst_services = ServiceDefinition.objects.filter(cluster=cluster)
            for service in lst_services:
                ans_services.append({
                    'uid': service.uid
                })
            
            # Append details
            ans_clusters.append({
                'services': ans_services,
                'uid': cluster.uid,
                'name': cluster.name
            })
        
        # Set to response
        response['status'] = 'ok'
        response['clusters'] = ans_clusters
    
    except Exception as ex:
        response['status'] = 'error'
        response['message'] = str(ex)
    
    # Fetch the function to call for the API call
    u_call = request.GET.get('call', 'iagent_cloudinfo')
    
    # Render response
    return uncache_response(HttpResponse( 
        u_call+'('+json.dumps( response )+');', 
        content_type = "application/javascript" ))


#@for_cloud
# Not under cloud restriction because it is accessed from Gateway server (anonymous user).
def api_get( request, cluster_uid ):
    
    # Try to find the cluster
    try:
        cluster = ClusterDefinition.objects.get( uid = cluster_uid )

        # Find the services
        i_services = {
            'fixed'     : ServiceDefinition.objects.filter( cluster = cluster, service_type = 'F' ),
            'scalable'  : ServiceDefinition.objects.filter( cluster = cluster, service_type = 'S' )
        }

        # Prepare response
        response = {
            'uid': cluster_uid,
            'services': {
                'fixed': { },
                'scalable': { }
            }
        }

        # Process services
        for s_type in ( 'fixed', 'scalable' ):
            for service in i_services[s_type]:
                
                # Build response
                response['services'][s_type][service.uid] = {
                     "offerings": {},
                    "template_uid": service.template.uid,
                    "context_uid": service.context.id,
                    "order": service.order
                }
            
                # Setu pofferings
                if service.disk_offering is not None:
                    response['services'][s_type][service.uid]["offerings"]["disk_uid"] = service.disk_offering.uid
                if service.network_offering is not None:
                    response['services'][s_type][service.uid]["offerings"]["network_uid"] = service.network_offering.uid
                if service.service_offering is not None:
                    response['services'][s_type][service.uid]["offerings"]["compute_uid"] = service.service_offering.uid
            
    except Exception as ex:
        response = { 'error': str(ex) }

    # Transform response contents
    json_contents = json.dumps( response ) 

    # Send response
    http_response = HttpResponse( json_contents, content_type = "application/json" )
    return http_response

##################################################
# Helpers
##################################################

def _newClusterUID( ):
    """
    Generates a new cluster UID
    """
    return uuid.uuid4().hex
    

def _splitServices( packed ):
    """
    Splits the service list (as submitted) into two sub-lists, based
    on the service_type value.
    
    If the service cas service_type = 'F' it will be placed on fixed.
    If it is 'S' it is placed on scalable.
    
    This function returns a tuple in (fixed[], scalable[]) format
    """
    fixed = []
    scalable = []
    
    for s_name in packed:
        service = packed[s_name]
        
        # Fixed?
        if service['service_type'] == 'F':
            fixed.append(service)
        
        # Scalable?
        elif service['service_type'] == 'S':
            scalable.append(service)

    # Return tuple
    return (fixed, scalable)

def _servicesToView( resultset ):
    """
    Convert the resultset in a view-friendly format. 
    This is used in order to have a unified data representation format.
    """
    result = { }
    for row in resultset:
        
        # Prepare basic
        ans_row = {
            # Direct mapping
            'uid': row.uid, 
            'min_instances': row.min_instances, 
            'order': row.order, 
            'service_type': row.service_type,
            
            # Reference names
            'context': row.context.name, 
            'template': row.template.name
        }
                
        # Set offerings
        if row.service_offering:
            ans_row['service_offering'] = row.service_offering
        if row.disk_offering:
            ans_row['disk_offering'] = row.disk_offering
        if row.network_offering:
            ans_row['network_offering'] = row.network_offering
        
        # Append result
        result[row.uid] = ans_row
    
    # Return the converted resultset
    return result

def _emptyValues():
    """
    Return an empty hash of parameters, ready to be passed to context editor
    """
    return {
        'protect': '',
        'secret': '',
        'name': '',
        'description': '',
        'services': { }
    }

def _getCreateViewContext():
    # Fill offerings and templates
    context = {
        "service_offerings": ServiceOffering.objects.all(),
        "disk_offerings": DiskOffering.objects.all(),
        "network_offerings": NetworkOffering.objects.all(),
        "templates": Template.objects.all(),        
    }
    if context["templates"].count() > 0:
        context["default_template"] = context["templates"][0].uid;
    if context["service_offerings"].count() > 0:
        context["default_service_offering"] = context["service_offerings"][0].uid;
    return context

def _createClusterDefinition(request, data):
    """
    Update or create a new cluster definition.
    """
    
    # Fetch/create record
    i_cluster = ClusterDefinition()
    
    print str(data)

    # Populate fields
    i_cluster.uid = _newClusterUID()
    i_cluster.name = str(data['name'])
    i_cluster.description = str(data['description'])
    i_cluster.public = False
    i_cluster.owner = request.user
    if 'protect' in data:
        i_cluster.key = str(data['secret'])
    
    # Trap errors during saving and/or population
    try:
        # Save cluster
        i_cluster.save()
    
        # Start creating services
        for name in data['services'].keys():
            service = data['services'][name]

            # Create instance
            i_service = ServiceDefinition()
        
            # Populate simple fields
            i_service.cluster = i_cluster
            i_service.service_type = str(service['service_type'])
            i_service.min_instances = int(service['min_instances'])
            i_service.order = int(service['order'])
            i_service.uid = str(service['uid'])
        
            # Polupate offerings
            if service['service_offering']:
                try:
                    i_offering = ServiceOffering.objects.get(name=str(service['service_offering']))
                except Exception as ex:
                    i_offering = None
                i_service.service_offering = i_offering
            
            if service['disk_offering']:
                try:
                    i_offering = DiskOffering.objects.get(name=str(service['disk_offering']))
                except Exception as ex:
                    i_offering = None
                i_service.disk_offering = i_offering

            if service['network_offering']:
                try:
                    i_offering = NetworkOffering.objects.get(name=str(service['network_offering']))
                except Exception as ex:
                    i_offering = None
                i_service.network_offering = i_offering
        
            # Populate template
            i_service.template = Template.objects.get(name=str(service['template']))
            i_service.context = ContextDefinition.objects.get(name=str(service['context']))
        
            # Save
            i_service.save()
            
    except Exception as ex:
        
        msg_error(request, "An exception occured: %s" % str(ex) )
        
        # An error occured
        return False
    
    # We are ready
    return True

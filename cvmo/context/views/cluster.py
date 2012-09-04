from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from cvmo.context.models import ServiceOffering, DiskOffering, NetworkOffering, \
    Template, ServiceDefinition, ClusterDefinition, ContextStorage,\
    ContextDefinition
from cvmo.querystring_parser import parser
import re
from cvmo.context.utils.context import salt_context_key, gen_context_key
import base64
from cvmo.context.utils import crypt
from cvmo.context.utils.views import render_confirm
from django.core.urlresolvers import reverse
from types import StringType

##################################################
# Request handlers
##################################################

def create( request ):
    """
        Cluster create view
    """
    
    # Send response
    return render_to_response( "pages/cluster_create.html", 
       __getCreateViewContext(), 
       RequestContext( request ) )

def save( request ):
    """
        Storage of cluster
    """
    
    # Get Values
    post_dict = parser.parse( request.POST.urlencode() )
    values = post_dict.get( 'values' )
    values = __transformCreateRequest( values )
    
    # Init. vars
    cluster = None
    services = []
    
    # Try to store request
    try:
        # Validate the request
        __validateCreateRequest( values )
        
        # Create the cluster
        cluster = ClusterDefinition()
        cluster.uid = gen_context_key()
        cluster.name = values["name"]
        cluster.description = values["description"]
        if "protect" in values \
            and values["protect"] \
            and values["secret"] is not "":
            cluster.key = salt_context_key( cluster.uid, values["secret"] )
        else:
            cluster.key = ""
        cluster.owner = request.user
        cluster.save()
        
        # Create services
        for service in values["services"]:
            ob = ServiceDefinition()
            ob.uid = service["uid"]
            ob.cluster = cluster
            ob.context = service["context"] 
            ob.template = service["template"] 
            ob.service_offering = service["service_offering"] 
            if service["disk_offering"] is not None:
                ob.disk_offering = service["disk_offering"]
            if service["network_offering"] is not None:             
                ob.network_offering = service["network_offering"]
            ob.save()
            services.append( ob )
             
    except Exception as ex:
        # Remove what partialy stored...        
        if cluster is not None:
            if len( services ) is not 0:
                for serv in services:
                    ob.delete()
            cluster.delete()
        
        # Show template again
        context = __getCreateViewContext()
        context["values"] = values
        context["msg_error"] = ex
        return render_to_response( "pages/cluster_create.html", 
           context, 
           RequestContext( request ) )
    
    # Go to dashboard
    request.session["redirect_msg_info"] = "Cluster was created successfully!"
    return redirect( "dashboard" )

def delete( request, cluster_id ):
    # Try to find the cluster
    try:
        cluster = ClusterDefinition.objects.get( id = cluster_id )
    except:
        request.session["redirect_msg_error"] = "Cluster with id " + cluster_id + " does not exist!"
        return redirect( "dashboard" )
                
    # Check if cluster belongs to calling user
    if request.user.id is not cluster.owner.id:
        request.session["redirect_msg_error"] = "Cluster with id " + cluster_id + " does not belong to you!"
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
        request.session["redirect_msg_info"] = "Cluster removed successfully!" 
        return redirect('dashboard')        
    else:
        # Show the confirmation screen
        return render_confirm( request, "Delete cluster", \
           "Are you sure you want to delete this cluster and it's services? This action is not undoable!", \
            reverse( 'cluster_delete', kwargs = { 'cluster_id': cluster_id } ) + '?confirm=yes', \
            reverse( 'dashboard' ) )

def api_get(request):
    pass

##################################################
# Helpers
##################################################

def __transformCreateRequest( values ):
    # Are there services?
    if "services" not in values:
        values["services"] = []
        return values
    
    # Single service bug fix
    if type( values["services"]["uid"] ) is StringType:
        for key in values["services"]:
            old_value = values["services"][key]
            values["services"][key] = [ old_value ]
            
    services = []            
    for i in range( len( values["services"]["uid"] ) ):
        # Create service form request values
        service = {}
        for key in values["services"]:
            service[key] = values["services"][key][i]
        
        # Get the objects
        try:
            service["context"] = ContextDefinition.objects.get(id=service["context_uid"])
        except:
            service["context"] = None
        try:
            service["template"] = Template.objects.get(uid=service["template_uid"])
        except:
            service["template"] = None
        try:
            service["service_offering"] = ServiceOffering.objects.get(uid=service["service_offering_uid"])
        except:
            service["service_offering"] = None
        if service["disk_offering_uid"] is not "":
            try: 
                service["disk_offering"] = DiskOffering.objects.get(uid=service["disk_offering_uid"])
            except:
                service["disk_offering"] = None
        else:
            service["disk_offering"] = None
        if service["network_offering_uid"] is not "":
            try:
                service["network_offering"] = NetworkOffering.objects.get(uid=service["network_offering_uid"])
            except:
                service["network_offering"] = None
        else:
            service["network_offering"] = None
        
        services.append( service )
        
    values["services"] = services
    return values

def __validateCreateRequest( values ):
    # Check basic
    if "name" not in values or values["name"] == "":
        raise Exception( "Name of cluster is required!" )
    if "services" not in values or len( values["services"] ) == 0:
        raise Exception( "Cluster services should be added!" )    
        
    # Check services
    i = 0
    for service in values["services"]:
        if service["uid"] == "":
            raise Exception( "Service " + ( i + 1 ) + " has not key defined..." )
        
        # Check template
        if service["template"] == None:
            raise Exception( "Service " + service["uid"] + " has not template defined..." )        
        
        # Check service offering
        if service["service_offering"] == None:
            raise Exception( "Service " + service["uid"] + " has not service offering defined..." )
        
        # Check context
        if service["context"] == None:
            raise Exception( "Service " + service["uid"] + " has not context defined..." )
        context_data = __getContextData( service["context_uid"], service["context_key"] )
        if context_data is None:
            raise Exception( "Service " + service["uid"] + " context is encrypted and provided key is invalid!" )
        
        # Check Other offerings
        if service["disk_offering_uid"] is not "" \
            and service["disk_offering"] is None:
            raise Exception( "Service " + service["uid"] + " disk offering does not exist." )
        if service["network_offering_uid"] is not "" \
            and service["network_offering"] is None:
            raise Exception( "Service " + service["uid"] + " network offering does not exist." )
            
        i += 1
        
def __getContextData( uid, key ):
    # Get Context data
    rows = ContextStorage.objects.filter(id=uid)
    if len( rows ) == 0:
        # Context not found...
        return None
    data = rows[0].data
    
    m = re.match( r"^ENCRYPTED:(.*)$", data )
    if m is not None:
        # Context is encrypted
        # Check key
        context = ContextDefinition.objects.get(id=uid)
        if context.key != salt_context_key( uid, key ):
            return None
        
        # Decrypt data
        dec_data = crypt.decrypt( base64.b64decode( m.group( 1 ) ), key )
        return dec_data    
    else:
        return data

def __getCreateViewContext():
    # Fill offerings and templates
    context = {
        "service_offerings": ServiceOffering.objects.all(),
        "disk_offerings": DiskOffering.objects.all(),
        "network_offerings": NetworkOffering.objects.all(),
        "templates": Template.objects.all(),        
    }        
    context["default_template"] = context["templates"][0].uid;
    context["default_service_offering"] = context["service_offerings"][0].uid;
    return context

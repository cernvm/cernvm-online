import json
import string
import hashlib
from datetime import datetime, timedelta
from random import sample, choice

from django.http import HttpResponse
from django.template import RequestContext
from django.utils.timezone import utc
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse

from cvmo.context.models import ClaimRequests, Machines, ContextDefinition, ContextStorage
from cvmo.context.utils.views import render_error, render_confirm, uncache_response

##############
REQUEST_TIMEOUT = timedelta(minutes=5)
##############

############################################
## Utility functions
############################################

def gen_key(length):
    # Easy-to-remember stuff...
    chars = '0123456789'
    return ''.join(choice(chars) for _ in range(length))

############################################
## API Entry points
############################################

def confirm(request):
    """ Second step in pairing sequence - Validate password """
    
    # Validate request
    if not 'REMOTE_ADDR' in request.META:
        return render_error(request, 400)
    if not 'uuid' in request.GET:
        return render_error(request, 400)
    if not 'pin' in request.GET:
        return render_error(request, 400)
    if not 'checksum' in request.GET:
        return render_error(request, 400)
    
    # Get some machine info
    ip = request.META['REMOTE_ADDR']
    uuid = request.GET['uuid']
    pin = request.GET['pin'].upper()
    checksum = request.GET['checksum']
    
    # Get our current timestamp and calculate validity time
    ts = datetime.utcnow().replace(tzinfo=utc)
    ts_expire = ts - REQUEST_TIMEOUT

    # Lookup the pin/machine UUID combination
    try:
        claim_request = ClaimRequests.objects.get(pin=pin, status='P', machine__uuid=uuid, alloc_date__gte=ts_expire)
        
        # Validate checksum
        if (claim_request.context.checksum != checksum):
            
            # Error...
            claim_request.status='E'
            claim_request.save()
            return uncache_response(HttpResponse('not-match', content_type="text/plain"))
        
        # If successful, claim it
        claim_request.status='C'
            
        # Machine is registered via pairing API
        claim_request.machine.status = 'P'
        
        # Save machine
        claim_request.save()

        # Return OK
        return uncache_response(HttpResponse('ok', content_type="text/plain"))
        
    except:
        # Something went wrong. Stop
        return uncache_response(HttpResponse('not-found', content_type="text/plain"))
    
def pair(request):
    """ First step in pairing sequence - Fetch context by pairing key """
    
    # Validate request
    if not 'REMOTE_ADDR' in request.META:
        return render_error(request, 400)
    if not 'uuid' in request.GET:
        return render_error(request, 400)
    if not 'pin' in request.GET:
        return render_error(request, 400)
    if not 'ver' in request.GET:
        return render_error(request, 400)
    
    # Get some machine info
    ip = request.META['REMOTE_ADDR']
    uuid = request.GET['uuid']
    pin = request.GET['pin'].upper()
    ver = request.GET['ver']
    
    # Get our current timestamp and calculate validity time
    ts = datetime.utcnow().replace(tzinfo=utc)
    ts_expire = ts - REQUEST_TIMEOUT
    
    # Lookup the pin
    try:
        claim_request = ClaimRequests.objects.get(pin=pin, status='U', alloc_date__gte=ts_expire)
    
        # Request is now claimed
        claim_request.status='C'
        
        # Unless the context is encrypted. Then we also need
        # a confirmation that the machine managed to decrypt it
        if (claim_request.context.key != ""):
            claim_request.status='P' # Pending
    
        # Get or create the VM
        claimed_vm = None
        try:
            claimed_vm = Machines.objects.get(uuid=uuid)

            # Update the IP address
            claimed_vm.ip = ip
            
            # If the owner is different than expected, someone tries to hijack...
            if (claimed_vm.owner != claim_request.requestby):
                claim_request.status='E'
                claim_request.save()
                return uncache_response(HttpResponse('invalid-pin', content_type="text/plain"))

        except:
            claimed_vm = Machines(uuid=uuid, ip=ip, version=ver, owner=claim_request.requestby)
    
        # Store the VM
        claim_request.machine = claimed_vm
            
        # Machine is registered via pairing API
        claimed_vm.status = 'P'
    
        # Update claim request
        claim_request.save()
    
        # Fetch the context definition
        claim_context = claim_request.context
        context_data = ContextStorage.objects.get(id=claim_context.id)
    
        # Update claimed VM info
        claimed_vm.context = claim_request.context
        claimed_vm.save()
        
        # Return successful pairing
        return uncache_response(HttpResponse(context_data.data, content_type="text/plain"))

    except:
        # Something went wrong. Stop
        return uncache_response(HttpResponse('invalid-pin', content_type="text/plain"))

def pair_status(request, claim_key):
    """ Poll the pairing status of a VM """
    _entry = ClaimRequests.objects.get(pin=claim_key)

    # Check the entry status
    status = 'unknown'
    if (_entry.status == 'C'): status='claimed'
    if (_entry.status == 'U'): status='unclaimed'
    if (_entry.status == 'P'): status='pending'
    if (_entry.status == 'E'): status='error'

    # Get our current timestamp and calculate validity time
    ts = datetime.utcnow().replace(tzinfo=utc)
    ts_expire = ts - REQUEST_TIMEOUT

    # Check for expired entry
    if (_entry.alloc_date < ts_expire):
        status='expired'

    # Send the response
    return uncache_response(HttpResponse('{"status":"'+status+'"}', content_type="application/json"))


def context_cloud(request):
    """ Two-in-one pairing and password validation phase """
    
    # Validate request
    if not 'REMOTE_ADDR' in request.META:
        return render_error(request, 400)
    if not 'uuid' in request.GET:
        return render_error(request, 400)
    if not 'context' in request.GET:
        return render_error(request, 400)
    if not 'ver' in request.GET:
        return render_error(request, 400)
    if not 'checksum' in request.GET:
        return render_error(request, 400)
    
    # Get some machine info
    ip = request.META['REMOTE_ADDR']
    uuid = request.GET['uuid']
    context_id = request.GET['context']
    ver = request.GET['ver']
    checksum = request.GET['checksum']
    
    # Validate password first
    try:
        context = ContextDefinition.objects.get(id=context_id)
        
        # Validate password
        if (context.key != "") and (checksum != context.key):
            return uncache_response(HttpResponse('invalid-checksum', content_type="text/plain"))
        
        # Register/update VM registration only if the VM is private
        if not context.public:
            
            # Get or create the VM
            claimed_vm = None
            try:
                claimed_vm = Machines.objects.get(uuid=uuid)
                claimed_vm.ip = ip
                claimed_vm.ver = ver
                claimed_vm.owner = context.owner
                
            except:
                claimed_vm = Machines(uuid=uuid, ip=ip, version=ver, owner=context.owner)
            
            # Machine is registered via cloud API
            claimed_vm.status = 'C'
            
            # Assign context
            claimed_vm.context = context
            claimed_vm.save()
        
        # Return the context definition
        context_data = ContextStorage.objects.get(id=context_id)
    
        # Return successful pairing
        return uncache_response(HttpResponse(context_data.data, content_type="text/plain"))
                    
    except:
        # Not found
        return uncache_response(HttpResponse('invalid-id', content_type="text/plain"))

############################################
## Template entry points
############################################

def pair_begin(request):
    # First screen of the pairing process: Show the available contextualization options
    return uncache_response(render_to_response('pages/machine_pair.html', {
            'context_list': ContextDefinition.objects.filter(owner=request.user),
            'context_public': ContextDefinition.objects.filter(public=True).exclude(owner=request.user)
        }, RequestContext(request)))
    

def pair_request(request, context_id):
    
    # Get our current timestamp - useful
    ts = datetime.utcnow().replace(tzinfo=utc)
    ts_expire = ts - REQUEST_TIMEOUT

    # Fetch the context definition for this pairing request
    context_definition = ContextDefinition.objects.get(id=context_id)
    
    # Lookup for previous entries that are not yet resolved
    entry = None
    prev_requests = ClaimRequests.objects.filter(requestby=request.user, status='U')
    for r in prev_requests:

        # Entry within validity frame?
        if (r.alloc_date >= ts_expire):
            
            # If we already have an entry... something went wrong. 
            if not entry == None:
                # Delete the entry
                r.delete()
            else:
                # Otherwise, that's the correct entry
                entry = r
                
                # Update the context definition
                entry.context = context_definition
                entry.save()
        
        else:
            # Take this opportunity to expire old sessions
            r.delete()
    
    # Generate key if no previous entry was found
    if entry == None:
        
        # Ensure that we don't have a pin collision (since our entropy is quite small)
        valid=0
        while valid == 0:
            key = gen_key(6)
            results = ClaimRequests.objects.filter(pin=key, status='U')
            if results.count() == 0:
                valid=1

        # Create an entry with unique PIN
        entry = ClaimRequests.objects.create(pin=key, status='U', alloc_date=ts, requestby=request.user, context=context_definition)
    
    # Show claim screen
    return uncache_response(render_to_response('pages/machine_pair_pin.html', {
        'key': entry.pin
    }, RequestContext(request)))


def pair_setup(request, claim_key):
    
    # Fetch claim information
    claim_request = ClaimRequests.objects.get(pin=claim_key)
    
    # Fetch the associated VM
    vm = claim_request.machine
    
    return uncache_response(render_to_response('pages/machine_setup.html', {
        'vm': vm
    }, RequestContext(request)))


def delete(request, machine_uuid):
    # Is it confirmed?
    if ('confirm' in request.GET) and (request.GET['confirm'] == 'yes'):
        # Delete the specified contextualization entry
        Machines.objects.filter(uuid=machine_uuid).delete()

        # Go to dashboard
        return redirect('dashboard')

    else:
        # Show the confirmation screen
        return uncache_response(render_confirm(request, 'Delete instance', 
                              'Are you sure you want to delete this virtual machine instance from you CernVM online account? This action is not undoable!',
                              reverse('vm_delete', kwargs={'machine_uuid':machine_uuid})+'?confirm=yes',
                              reverse('dashboard')
                              ))

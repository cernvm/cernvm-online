import json
import logging
from datetime import datetime, timedelta
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.utils.timezone import utc
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from cvmo.context.models import ContextDefinition, ContextStorage
from cvmo.cluster.models import ClusterDefinition
from cvmo.vm.models import ClaimRequests, Machines
from cvmo.core.utils.views import render_confirm, uncache_response
from cvmo.core.utils.context import gen_pin, get_uuid_salt
from django.db.models.query_utils import Q

REQUEST_TIMEOUT = timedelta(minutes=5)

#
# Views
#


def pair_begin(request):
    # First screen of the pairing process: Show the available
    # contextualization options
    return uncache_response(
        render(
            request,
            "vm/machine_pair.html",
            {
                "context_list": ContextDefinition.objects.filter(
                    Q(owner=request.user)
                    & Q(inherited=False)
                    & Q(abstract=False)
                ),
                "context_public": ContextDefinition.objects.filter(
                    public=True
                ).exclude(owner=request.user)
            }
        )
    )


def pair_request(request, context_id):
    # Get our current timestamp - useful
    ts = datetime.utcnow().replace(tzinfo=utc)
    ts_expire = ts - REQUEST_TIMEOUT

    # Fetch the context definition for this pairing request
    context_definition = ContextDefinition.objects.get(id=context_id)

    # Destroy all previous requests in pending state
    ClaimRequests.objects.filter(requestby=request.user, status="U").delete()

    # Ensure that we don"t have a pin collision (since our entropy is quite
    # small)
    valid = 0
    while valid == 0:
        key = gen_pin(6, (context_definition.key != ""),
                      get_uuid_salt(context_definition.id))
        results = ClaimRequests.objects.filter(pin=key, status="U")
        if results.count() == 0:
            valid = 1

    # Create an entry with unique PIN
    entry = ClaimRequests.objects.create(
        pin=key, status="U", alloc_date=ts, requestby=request.user,
        context=context_definition
    )

    # Show claim screen
    return uncache_response(
        render(request, "vm/machine_pair_pin.html", {"key": entry.pin})
    )


def pair_setup(request, claim_key):
    # Fetch claim information
    claim_request = ClaimRequests.objects.get(pin=claim_key)
    # Fetch the associated VM
    vm = claim_request.machine
    return uncache_response(
        render(request, "vm/machine_setup.html", {"vm": vm})
    )


def delete(request, machine_uuid):
    # Is it confirmed?
    if ("confirm" in request.GET) and (request.GET["confirm"] == "yes"):
        # Delete the specified contextualization entry
        Machines.objects.filter(uuid=machine_uuid).delete()
        # Go to dashboard
        return redirect("dashboard")
    else:
        # Show the confirmation screen
        return uncache_response(
            render_confirm(
                request,
                "Delete instance",
                "Are you sure you want to delete this virtual machine instance\
 from you CernVM online account? This action is not undoable!",
                reverse(
                    "vm_delete", kwargs={"machine_uuid": machine_uuid}
                ) + "?confirm=yes",
                reverse("dashboard")
            )
        )


def pair_status(request, claim_key):
    """ Poll the pairing status of a VM """
    _entry = ClaimRequests.objects.get(pin=claim_key)

    # Check the entry status
    status = "unknown"
    if (_entry.status == "C"):
        status = "claimed"
    if (_entry.status == "U"):
        status = "unclaimed"
    if (_entry.status == "P"):
        status = "pending"
    if (_entry.status == "E"):
        status = "error"

    # Get our current timestamp and calculate validity time
    ts = datetime.utcnow().replace(tzinfo=utc)
    ts_expire = ts - REQUEST_TIMEOUT

    # Check for expired entry
    if (_entry.alloc_date < ts_expire):
        status = "expired"

    # Send the response
    return uncache_response(
        HttpResponse(
            json.dumps({"status": status}), content_type="application/json"
        )
    )

#
# API Entry points
#


def context_fetch(request):
    """
    First step in pairing or contextualization sequence
    """
    l = logging.getLogger("cvmo")

    # Validate request
    if not "REMOTE_ADDR" in request.META:
        l.log(logging.ERROR, "`REMOTE_ADDR` not found")
        raise SuspiciousOperation("`REMOTE_ADDR` not found")
    if not "uuid" in request.GET:
        l.log(logging.ERROR, "`uuid` is required")
        raise SuspiciousOperation("`uuid` is required")
    if not "ver" in request.GET:
        l.log(logging.ERROR, "`ver` is required")
        raise SuspiciousOperation("`ver` is required")
    if (not "pin" in request.GET) and (not "context_id" in request.GET):
        l.log(logging.ERROR, "`pin` is required")
        raise SuspiciousOperation("`pin` is required")
    if not "checksum" in request.GET:
        l.log(logging.ERROR, "`checksum` is required")
        raise SuspiciousOperation("`checksum` is required")

    # Fetch some helpful variables from the request
    checksum = request.GET["checksum"]
    uuid = request.GET["uuid"]
    ver = request.GET["ver"]
    ip = _source_ip(request)

    # Check if we are using PIN or CONTEXT_ID
    if ("pin" in request.GET):
        return _context_fetch_pin(request.GET["pin"], checksum, uuid, ip, ver)
    elif ("context_id" in request.GET):
        return _context_fetch_context_id(request.GET["context_id"], checksum,
                                         uuid, ip, ver)


def _context_fetch_pin(pin, checksum, uuid, ip, ver):
    # Get our current timestamp and calculate validity time
    ts = datetime.utcnow().replace(tzinfo=utc)
    ts_expire = ts - REQUEST_TIMEOUT

    # Lookup the pin
    try:
        claim_request = ClaimRequests.objects.get(
            pin=pin, status="U", alloc_date__gte=ts_expire
        )
        # If the request is encrypted, make sure the user knows how to
        # decrypt it
        if (claim_request.context.key != ""):
            if (claim_request.context.key != checksum):
                return uncache_response(
                    HttpResponse(
                        "invalid-checksum", content_type="text/plain"
                    )
                )
        # Request is now claimed
        claim_request.status = "C"

        # Get or create the VM
        claimed_vm = None
        try:
            claimed_vm = Machines.objects.get(uuid=uuid)
            # Update the IP address
            claimed_vm.ip = ip
            # If the owner is different than expected, someone tries to
            # hijack...
            if (claimed_vm.owner != claim_request.requestby):
                claim_request.status = "E"
                claim_request.save()
                return uncache_response(
                    HttpResponse(
                        "not-authorized", content_type="text/plain"
                    )
                )
        except:
            claimed_vm = Machines(
                uuid=uuid, ip=ip, version=ver,
                owner=claim_request.requestby
            )

        # Store the VM
        claim_request.machine = claimed_vm
        # Machine is registered via pairing API
        claimed_vm.status = "P"
        # Update claim request
        claim_request.save()

        # Fetch the context definition
        claim_context = claim_request.context
        context_data = ContextStorage.objects.get(id=claim_context.id)

        # Update claimed VM info
        claimed_vm.context = claim_request.context
        claimed_vm.save()

        # Return successful pairing
        return uncache_response(
            HttpResponse(context_data.data, content_type="text/plain")
        )
    except:
        # Something went wrong. Stop
        return uncache_response(
            HttpResponse("not-found", content_type="text/plain")
        )


def _context_fetch_context_id(context_id, checksum, uuid, ip, ver):
    context = None
    cluster = None

    try:
        context = ContextDefinition.objects.get(id=context_id)
        owner = context.owner

        # If the context is encrypted, make sure the user knows how to
        # decrypt it
        if (context and context.key != ""):
            if (context.key != checksum):
                return uncache_response(
                    HttpResponse("invalid-checksum", content_type="text/plain")
                )
    except ContextDefinition.DoesNotExist:
        cluster = ClusterDefinition.objects.get(
            deployable_context_id=context_id
        )
        owner = cluster.owner
    except ClusterDefinition.DoesNotExist:
        return HttpResponse("not-found", content_type="text/plain")

    # Register/update VM registration only if the VM is private
    if (context and not context.public) or cluster:
        try:
            claimed_vm = Machines.objects.get(uuid=uuid)
            claimed_vm.ip = ip
            claimed_vm.ver = ver
            claimed_vm.owner = owner
        except Machines.DoesNotExist:
            claimed_vm = Machines(
                uuid=uuid, ip=ip, version=ver, owner=owner
            )
        if context:
            claimed_vm.status = "C"  # Machine is registered via cloud API
            claimed_vm.context = context
        if cluster:
            claimed_vm.status = "E"  # Machine is registered via cloud API
            claimed_vm.context = cluster.master_context
        claimed_vm.save()

    # Return the context definition
    context_data = ContextStorage.objects.get(id=context_id)
    return HttpResponse(context_data.data, content_type="text/plain")


#
# Helpers
#


def _source_ip(request):
    """ Try to detect the real source IP """
    if "HTTP_X_FORWARDED_FOR" in request.META:

        # Fetch the proxy headers
        ip = request.META["HTTP_X_FORWARDED_FOR"]

        # Get the very first ip if we have a list
        if "," in ip:
            ip = ip.split(", ")[0]

    else:
        ip = request.META["REMOTE_ADDR"]

    # Return the guessed IP
    return ip

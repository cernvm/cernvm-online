from django.conf.urls import patterns, url

urlpatterns = patterns(
    "cvmo.vm.views",
    url(r"^pair/$", "pair_begin", name="vm_pair_begin"),
    url(r"^pair/(?P<context_id>[-\w]+)$", "pair_request",
        name="vm_pair_request"),
    url(r"^setup/(?P<claim_key>\w+)$", "pair_setup", name="vm_setup"),
    url(r"^delete/(?P<machine_uuid>[-\w]+)$", "delete", name="vm_delete"),
    url(r"^ajax/machine/status/(?P<claim_key>\w+)$", "pair_status",
        name="vm_ajax_status"),
    url(r"^api/fetch$", "context_fetch"),
    url(r"^api/context$", "context_fetch")
)

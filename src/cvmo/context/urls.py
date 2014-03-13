from django.conf.urls import patterns, url

#
# Context
#

urlpatterns = patterns(
    "cvmo.context.views.context",

    # Context creation
    url(r"/new$", "blank", name="context_new"),
    url(r"/create$", "create", name="context_create"),

    # Context cloning
    url(r"/clone/(?P<context_id>[-\w]+)$", "clone",
        name="context_clone"),
    # url(r"clone/(?P<context_id>[-\w]+)/simple/*$",
    #     "context_from_abstract", {"cloning": True},
    #     name="context_clone_simple"),

    # Removal of context
    url(r"/delete/(?P<context_id>[-\w]+)$", "delete",
        name="context_delete"),

    # Used from the webpage to show contexts. If encrypted, they interactively
    # ask for a password
    url(r"/view/(?P<context_id>[-\w]+)$", "view", name="context_view"),
    url(r"/view/(?P<context_id>[-\w]+)/json/*$", "api_get",
        {"format": "json", "askpass": True}, name="context_view_json"),
    url(r"/view/(?P<context_id>[-\w]+)/plain/*$", "api_get",
        {"format": "plain", "askpass": True}, name="context_view_plain"),
    url(r"/view/(?P<context_id>[-\w]+)/raw/*$", "api_get",
        {"format": "raw", "askpass": True}, name="context_view_raw")
)

#
# Abstract context
#

# urlpatterns = patterns(
#     "cvmo.context.views.abstract",
#     url(r"abstract/new$", "blank_abstract", name="abstract_new"),
#     url(r"abstract/create$", "create_abstract", name="abstract_create"),
#     url(r"abstract/clone/(?P<context_id>[-\w]+)$", "clone_abstract",
#         name="abstract_clone"),
#     url(r"abstract/contextualize/(?P<context_id>[-\w]+)$",
#         "context_from_abstract", name="abstract_contextualize")
# )


# API interface. No interactive password prompt: in raw contexts decryption occurs on the client
# url(r"api/(?P<context_id>[-\w]+)/*$", "api_get", {"format": "raw", "askpass": False}, name="context_api_encoded"),
# url(r"api/(?P<context_id>[-\w]+)/plain/*$", "api_get", {"format": "plain", "askpass": False}, name="context_api_plain"),

# url(r"ajax/list/*$", "ajax_list", name="vm_ajax_listcontexts"),
# url(r"ajax/publish/*$", "ajax_publish_context", name="ajax_publish_context"),
# url(r"ajax/abstract/list/*$", "ajax_abstract_list", name="ajax_abstract_list"),
# )

# urlpatterns += patterns("cvmo.context.views.machine",
# url(r"machine/pair/$", "pair_begin", name="vm_pair_begin"),
# url(r"machine/pair/(?P<context_id>[-\w]+)$", "pair_request", name="vm_pair_request"),
# url(r"machine/setup/(?P<claim_key>\w+)$", "pair_setup", name="vm_setup"),
# url(r"machine/delete/(?P<machine_uuid>[-\w]+)$", "delete", name="vm_delete"),
# url(r"ajax/machine/status/(?P<claim_key>\w+)$", "pair_status", name="vm_ajax_status"),
# url(r"api/fetch$", "context_fetch"),
# url(r"api/context$", "context_fetch")
# )

# urlpatterns += patterns("cvmo.context.views.actions",
# url(r"actions/edit$", "edit", name="actions_edit"),
# url(r"actions/save$", "save", name="actions_save")
# )

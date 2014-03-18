from django.conf.urls import patterns, url

#
# Context
#

urlpatterns = patterns(
    "cvmo.context.views.context",

    # Context creation
    url(r"^new$", "blank", name="context_new"),
    url(r"^create$", "create", name="context_create"),

    # Context cloning
    url(r"^clone/(?P<context_id>[-\w]+)$", "clone",
        name="context_clone"),

    # Removal of context
    url(r"^delete/(?P<context_id>[-\w]+)$", "delete",
        name="context_delete"),

    # Used from the webpage to show contexts. If encrypted, they interactively
    # ask for a password
    url(r"^view/(?P<context_id>[-\w]+)$", "view", name="context_view"),
    url(r"^view/(?P<context_id>[-\w]+)/json/*$", "api_get",
        {"format": "json", "askpass": True}, name="context_view_json"),
    url(r"^view/(?P<context_id>[-\w]+)/plain/*$", "api_get",
        {"format": "plain", "askpass": True}, name="context_view_plain"),
    url(r"^view/(?P<context_id>[-\w]+)/raw/*$", "api_get",
        {"format": "raw", "askpass": True}, name="context_view_raw"),
    url(r"^ajax/publish/*$", "ajax_publish_context",
        name="context_ajax_publish_context"),
    url(r"^ajax/list$", "ajax_get_list", name="context_ajax_get_list")
)

#
# Abstract context
#

urlpatterns += patterns(
    "cvmo.context.views.abstract",

    url(r"^abstract/new$", "blank_abstract", name="context_abstract_new"),
    url(r"^abstract/create$", "create_abstract",
        name="context_abstract_create"),
    url(r"^abstract/contextualize/(?P<context_id>[-\w]+)$",
        "context_from_abstract", name="context_abstract_contextualize"),
    url(r"^abstract/clone/(?P<context_id>[-\w]+)$",
        "clone_abstract", name="context_abstract_clone"),
    url(r"^ajax/abstract/list/*$", "ajax_abstract_list",
        name="context_ajax_abstract_list")
)


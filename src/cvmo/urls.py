from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from cvmo.settings import URL_PREFIX

#
# Home UI
#

urlpatterns = patterns("cvmo.context.views.index",
    url(r"^%s$" % URL_PREFIX, "welcome", name="welcome"),
    url(r"^%stest$" % URL_PREFIX, "test"),
    url(r"^%sdashboard$" % URL_PREFIX, "dashboard", name="dashboard")
)

#
# User UI
#

urlpatterns += patterns(
    "", url(r"^%suser/" % URL_PREFIX, include("cvmo.user.urls"))
)

#
# Admin UI
#

# admin.autodiscover()
urlpatterns += patterns("",
    url(r"^%sadmin/" % URL_PREFIX, include(admin.site.urls)),
)

#
# DEBUG: Serve media files
#

if settings.DEBUG is True:
    urlpatterns += patterns("",
        url(
            r"^%smedia/(?P<path>.*)$" % URL_PREFIX,
            "django.views.static.serve",
            {
                "document_root": settings.MEDIA_ROOT,
                "show_indexes": True
            }
        )
    )

# urlpatterns += patterns("cvmo.context.views.context",
#     url(r"^" + URL_PREFIX + "abstract/new$", "blank_abstract",  name="abstract_new"),
#     url(r"^" + URL_PREFIX + "abstract/create$", "create_abstract", name="abstract_create"),
#     url(r"^" + URL_PREFIX + "abstract/clone/(?P<context_id>[-\w]+)$", "clone_abstract", name="abstract_clone"),
#     url(r"^" + URL_PREFIX + "abstract/contextualize/(?P<context_id>[-\w]+)$", "context_from_abstract", name="abstract_contextualize"),
#     url(r"^" + URL_PREFIX + "context/new$",                        "blank",       name="context_new"),
#     url(r"^" + URL_PREFIX + "context/create$",                     "create",      name="context_create"),
#     url(r"^" + URL_PREFIX + "context/clone/(?P<context_id>[-\w]+)$", "clone",     name="context_clone"),
#     url(r"^" + URL_PREFIX + "context/clone/(?P<context_id>[-\w]+)/simple/*$", "context_from_abstract", {"cloning": True}, name="context_clone_simple"),
#     url(r"^" + URL_PREFIX + "context/delete/(?P<context_id>[-\w]+)$", "delete",   name="context_delete"),
#     url(r"^" + URL_PREFIX + "context/view/(?P<context_id>[-\w]+)$",   "view",     name="context_view"),

# Used from the webpage to show contexts. If encrypted, they interactively ask for a password
#     url(r"^" + URL_PREFIX + "context/view/(?P<context_id>[-\w]+)/json/*$", "api_get", {"format": "json", "askpass": True}, name="context_view_json"),
#     url(r"^" + URL_PREFIX + "context/view/(?P<context_id>[-\w]+)/plain/*$", "api_get", {"format": "plain", "askpass": True}, name="context_view_plain"),
#     url(r"^" + URL_PREFIX + "context/view/(?P<context_id>[-\w]+)/raw/*$", "api_get", {"format": "raw", "askpass": True}, name="context_view_raw"),

# API interface. No interactive password prompt: in raw contexts decryption occurs on the client
#     url(r"^" + URL_PREFIX + "api/context/(?P<context_id>[-\w]+)/*$", "api_get", {"format": "raw", "askpass": False}, name="context_api_encoded"),
#     url(r"^" + URL_PREFIX + "api/context/(?P<context_id>[-\w]+)/plain/*$", "api_get", {"format": "plain", "askpass": False}, name="context_api_plain"),

#     url(r"^" + URL_PREFIX + "ajax/context/list/*$", "ajax_list",                    name="vm_ajax_listcontexts"),
#     url(r"^" + URL_PREFIX + "ajax/context/publish/*$", "ajax_publish_context", name="ajax_publish_context"),
#     url(r"^" + URL_PREFIX + "ajax/abstract/list/*$", "ajax_abstract_list", name="ajax_abstract_list"),
# )

# urlpatterns += patterns("cvmo.context.views.machine",
#     url(r"^" + URL_PREFIX + "machine/pair/$", "pair_begin", name="vm_pair_begin"),
#     url(r"^" + URL_PREFIX + "machine/pair/(?P<context_id>[-\w]+)$", "pair_request", name="vm_pair_request"),
#     url(r"^" + URL_PREFIX + "machine/setup/(?P<claim_key>\w+)$", "pair_setup", name="vm_setup"),
#     url(r"^" + URL_PREFIX + "machine/delete/(?P<machine_uuid>[-\w]+)$", "delete", name="vm_delete"),
#     url(r"^" + URL_PREFIX + "ajax/machine/status/(?P<claim_key>\w+)$", "pair_status", name="vm_ajax_status"),
#     url(r"^" + URL_PREFIX + "api/fetch$", "context_fetch"),
#     url(r"^" + URL_PREFIX + "api/context$", "context_fetch")
# )

# urlpatterns += patterns("cvmo.context.views.actions",
#     url(r"^" + URL_PREFIX + "actions/edit$", "edit",                  name="actions_edit"),
#     url(r"^" + URL_PREFIX + "actions/save$", "save",                  name="actions_save")
# )

# Marketplace
# urlpatterns += patterns("cvmo.context.views.marketplace",
#     url(r"^" + URL_PREFIX + "market/revoke/(?P<context_id>[-\w]+)$", "revoke", name="market_revoke"),
#     url(r"^" + URL_PREFIX + "market/publish/(?P<context_id>[-\w]+)$", "publish", name="market_publish"),
#     url(r"^" + URL_PREFIX + "market/publish.do$", "publish_action",   name="market_publish_action"),
#     url(r"^" + URL_PREFIX + "market/list$", "list",                   name="market_list"),
#     url(r"^" + URL_PREFIX + "market/list.search$", "list_ajax",       name="market_list_search"),
#     url(r"^" + URL_PREFIX + "market/vote.do$", "vote_ajax",           name="market_vote"),
# )

# Check if cloud is enabled
# if settings.ENABLE_CLOUD:
#     urlpatterns += patterns("cvmo.context.views.marketplace",
#         url(r"^" + URL_PREFIX + "market/cluster_revoke/(?P<cluster_id>[-\w]+)$", "cluster_revoke", name="market_cluster_revoke"),
#         url(r"^" + URL_PREFIX + "market/cluster_publish/(?P<cluster_id>[-\w]+)$", "cluster_publish", name="market_cluster_publish"),
#         url(r"^" + URL_PREFIX + "market/cluster_publish.do$", "cluster_publish_action",   name="market_cluster_publish_action"),
#         url(r"^" + URL_PREFIX + "api/market/search.clusters$", "list_cluster_ajax",   name="market_list_cluster_ajax"),
#         url(r"^" + URL_PREFIX + "api/market/groups$", "list_cluster_groups",   name="market_list_cluster_groups"),
#     )

# Optional 1) Cluster defintion
# if settings.ENABLE_CLOUD:
#     urlpatterns += patterns("cvmo.context.views.cluster",
#         url(r"^" + URL_PREFIX + "cluster/create$", "create", name="cluster_create"),
#         url(r"^" + URL_PREFIX + "cluster/create.do$", "do_create", name="cluster_create_action"),
#         url(r"^" + URL_PREFIX + "cluster/delete/(?P<cluster_id>[-\w]+)$","delete", name="cluster_delete"),
#         url(r"^" + URL_PREFIX + "cluster/view/(?P<cluster_id>[-\w]+)$","view", name="cluster_view"),
#         url(r"^" + URL_PREFIX + "cluster/clone/(?P<cluster_id>[-\w]+)$","clone",name="cluster_clone"),
#         url(r"^" + URL_PREFIX + "api/cluster/(?P<cluster_uid>[-\w]*)/{0,1}$", "api_get"),
#         url(r"^" + URL_PREFIX + "api/cloudinfo\.js$", "api_cloudinfo"),
#      )

from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('cvmo.context.views.index',
    url(r'^$', 'welcome', name="welcome"),
    url(r'^test$', 'test'),
    url(r'^dashboard$', 'dashboard', name="dashboard")
)

# DEBUGG
urlpatterns += patterns("",
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
    )

urlpatterns += patterns('cvmo.context.views.context',
    url(r'^abstract/new$', 'blank_abstract',  name="abstract_new"),
    url(r'^abstract/create$', 'create_abstract', name="abstract_create"),
    url(r'^abstract/clone/(?P<context_id>[-\w]+)$', 'clone_abstract', name="abstract_clone"),
    url(r'^abstract/contextualize/(?P<context_id>[-\w]+)$', 'context_from_abstract', name="abstract_contextualize"),
    url(r'^context/new$',                        'blank',       name="context_new"),
    url(r'^context/create$',                     'create',      name="context_create"),
    url(r'^context/clone/(?P<context_id>[-\w]+)$', 'clone',     name="context_clone"),
    url(r'^context/clone/(?P<context_id>[-\w]+)/simple/*$', 'context_from_abstract', {'cloning': True}, name="context_clone_simple"),
    url(r'^context/delete/(?P<context_id>[-\w]+)$', 'delete',   name="context_delete"),
    url(r'^context/view/(?P<context_id>[-\w]+)$',   'view',     name="context_view"),

    # Used from the webpage to show contexts. If encrypted, they interactively ask for a password
    url(r'^context/view/(?P<context_id>[-\w]+)/json/*$', 'api_get', {'format': 'json', 'askpass': True}, name='context_view_json'),
    url(r'^context/view/(?P<context_id>[-\w]+)/plain/*$', 'api_get', {'format': 'plain', 'askpass': True}, name='context_view_plain'),
    url(r'^context/view/(?P<context_id>[-\w]+)/raw/*$', 'api_get', {'format': 'raw', 'askpass': True}, name='context_view_raw'),

    # API interface. No interactive password prompt: in raw contexts decryption occurs on the client
    url(r'^api/context/(?P<context_id>[-\w]+)/*$', 'api_get', {'format': 'raw', 'askpass': False}, name='context_api_encoded'),
    url(r'^api/context/(?P<context_id>[-\w]+)/plain/*$', 'api_get', {'format': 'plain', 'askpass': False}, name='context_api_plain'),

    url(r'^ajax/context/list/*$', 'ajax_list',                    name="vm_ajax_listcontexts"),
    url(r'^ajax/context/publish/*$', 'ajax_publish_context', name="ajax_publish_context"),
    url(r'^ajax/abstract/list/*$', 'ajax_abstract_list', name="ajax_abstract_list"),
)

urlpatterns += patterns('cvmo.context.views.machine',
    url(r'^machine/pair/$', 'pair_begin', name="vm_pair_begin"),
    url(r'^machine/pair/(?P<context_id>[-\w]+)$', 'pair_request', name="vm_pair_request"),
    url(r'^machine/setup/(?P<claim_key>\w+)$', 'pair_setup', name="vm_setup"),
    url(r'^machine/delete/(?P<machine_uuid>[-\w]+)$', 'delete', name="vm_delete"),
    url(r'^ajax/machine/status/(?P<claim_key>\w+)$', 'pair_status', name="vm_ajax_status"),
    url(r'^api/fetch$', 'context_fetch'),
    url(r'^api/context$', 'context_fetch')
)

urlpatterns += patterns('cvmo.context.views.user',
    url(r'^login$', 'login',                        name="login"),
    url(r'^login_action', 'login_action',           name="do_login"),
    url(r'^register$', 'register',                  name="register"),
    url(r'^register_action$', 'register_action',    name="do_register"),
    url(r'^logout$', 'logout',                      name="logout"),
    url(r'^profile$', 'profile_edit',               name="profile"),
    url(r'^profile_save$', 'profile_edit_action',   name="profile_save"),
    url(r'^account_activation$', 'account_activation', name="account_activation"),
    url(r'^user/bulk$', 'bulk_add',                 name="bulk_add"),
    url(r'^user/bulkcommit$', 'bulk_add_commit',    name="bulk_add_commit")
)

urlpatterns += patterns('cvmo.context.views.actions',
    url(r'^actions/edit$', 'edit',                  name="actions_edit"),
    url(r'^actions/save$', 'save',                  name="actions_save")
)


# Optional 1) Cluster defintion
if settings.ENABLE_CLOUD:
    urlpatterns += patterns('cvmo.context.views.cluster',
        url(r'^cluster/create$', 'create', name="cluster_create"),
        url(r'^cluster/create.do$', 'do_create', name="cluster_create_action"),
        url(r'^cluster/delete/(?P<cluster_id>[-\w]+)$','delete', name="cluster_delete"),
        url(r'^cluster/view/(?P<cluster_id>[-\w]+)$','view', name="cluster_view"),
        url(r'^cluster/clone/(?P<cluster_id>[-\w]+)$','clone',name='cluster_clone'),
        url(r'^api/cluster/(?P<cluster_uid>[-\w]*)/{0,1}$', 'api_get'),
        url(r'^api/cloudinfo\.js$', 'api_cloudinfo'),
     )

# Optional 2) CSC Login
if settings.ENABLE_CSC:
    urlpatterns += patterns('cvmo.context.views.csc',
        url(r'^csc$', 'csc_login',                  name="csc_login"),
        url(r'^csc/do_login$', 'csc_do_login',      name="csc_do_login")
    )

# Optional 3) Marketplace
if settings.ENABLE_MARKET:
    urlpatterns += patterns('cvmo.context.views.marketplace',
        url(r'^market/revoke/(?P<context_id>[-\w]+)$', 'revoke', name="market_revoke"),
        url(r'^market/publish/(?P<context_id>[-\w]+)$', 'publish', name="market_publish"),
        url(r'^market/publish.do$', 'publish_action',   name="market_publish_action"),
        url(r'^market/list$', 'list',                   name="market_list"),
        url(r'^market/list.search$', 'list_ajax',       name="market_list_search"),
        url(r'^market/vote.do$', 'vote_ajax',           name="market_vote"),
        url(r'^marketplace$', 'marketplace', name='marketplace'),
        url(r'^marketplace_detail/(?P<id>.*)/$', 'marketplace_detail', name='marketplace_list'),
        url(r'^import_to_dashboard/(?P<id>[-\w]+)$', 'import_to_dashboard', name="import_to_dashboard"),
    )
    
    # Check if cloud is enabled
    if settings.ENABLE_CLOUD:
        urlpatterns += patterns('cvmo.context.views.marketplace',
            url(r'^market/cluster_revoke/(?P<cluster_id>[-\w]+)$', 'cluster_revoke', name="market_cluster_revoke"),
            url(r'^market/cluster_publish/(?P<cluster_id>[-\w]+)$', 'cluster_publish', name="market_cluster_publish"),
            url(r'^market/cluster_publish.do$', 'cluster_publish_action',   name="market_cluster_publish_action"),
            url(r'^api/market/search.clusters$', 'list_cluster_ajax',   name="market_list_cluster_ajax"),
            url(r'^api/market/groups$', 'list_cluster_groups',   name="market_list_cluster_groups"),
        )

# Admin UI
urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^search/', include('haystack.urls')), 
)

# Wiki pages
urlpatterns += patterns( "cvmo.wiki.views",    
    url( r"^wiki/(?P<url>.*)\.[^.]*$", "show_wiki" ),
    url( r"^wiki/(?P<url>.*)$", "show_wiki" )
)


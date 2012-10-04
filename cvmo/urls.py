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

urlpatterns += patterns('cvmo.context.views.context',
    url(r'^context/new$',                        'blank',       name="context_new"),
    url(r'^context/create$',                     'create',      name="context_create"),
    url(r'^context/clone/(?P<context_id>[-\w]+)$', 'clone',     name="context_clone"),
    url(r'^context/delete/(?P<context_id>[-\w]+)$', 'delete',   name="context_delete"),
    url(r'^context/view/(?P<context_id>[-\w]+)$',   'view',     name="context_view"),
    url(r'^api/context/(?P<context_id>[-\w]+)/$', 'api_get'),
    url(r'^ajax/context/list$', 'ajax_list',                    name="vm_ajax_listcontexts"),
)

urlpatterns += patterns('cvmo.context.views.machine',
    url(r'^machine/pair/$', 'pair_begin', name="vm_pair_begin"),
    url(r'^machine/pair/(?P<context_id>[-\w]+)$', 'pair_request', name="vm_pair_request"),
    url(r'^machine/setup/(?P<claim_key>\w+)$', 'pair_setup', name="vm_setup"),
    url(r'^machine/delete/(?P<machine_uuid>[-\w]+)$', 'delete', name="vm_delete"),
    url(r'^ajax/machine/status/(?P<claim_key>\w+)$', 'pair_status', name="vm_ajax_status"),
    url(r'^api/fetch$', 'context_fetch')
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
        url(r'^cluster/save$', 'save', name="cluster_save"),
        url(r'^cluster/delete/(?P<cluster_id>[-\w]+)$','delete', name="cluster_delete"),
        url(r'^api/cluster/(?P<cluster_uid>[-\w]*)/{0,1}$', 'api_get'),
        url(r'^api/cloudinfo\.js$', 'api_cloudinfo'),
     )

# Optional 2) CSC Login
if (settings.ENABLE_CSC):
    urlpatterns += patterns('cvmo.context.views.csc',
        url(r'^csc$', 'csc_login',                  name="csc_login"),
        url(r'^csc/do_login$', 'csc_do_login',      name="csc_do_login")
    )

# Admin UI
urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),    
)

# Wiki pages
urlpatterns += patterns( "cvmo.wiki.views",    
    url( r"^wiki/(?P<url>.*)\.[^.]*$", "show_wiki" ),
    url( r"^wiki/(?P<url>.*)$", "show_wiki" )
)


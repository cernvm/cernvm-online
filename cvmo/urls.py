from django.conf.urls import patterns, include, url

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

urlpatterns += patterns('cvmo.context.views.cluster',
    url(r'^cluster/new$',                          'blank',     name="cluster_new"),
    url(r'^cluster/create$',                       'create',    name="cluster_create"),
    url(r'^cluster/clone/(?P<cluster_id>[-\w]+)$', 'clone',     name="cluster_clone"),
    url(r'^cluster/delete/(?P<cluster_id>[-\w]+)$','delete',    name="cluster_delete"),
    url(r'^cluster/view/(?P<cluster_id>[-\w]+)$',  'view',      name="cluster_view"),
    url(r'^api/cluster/(?P<cluster_id>[-\w]+)/$',  'api_get')
)

urlpatterns += patterns('cvmo.context.views.machine',
    url(r'^machine/pair/$', 'pair_begin', name="vm_pair_begin"),
    url(r'^machine/pair/(?P<context_id>[-\w]+)$', 'pair_request', name="vm_pair_request"),
    url(r'^machine/setup/(?P<claim_key>\w+)$', 'pair_setup', name="vm_setup"),
    url(r'^machine/delete/(?P<machine_uuid>[-\w]+)$', 'delete', name="vm_delete"),
    url(r'^ajax/machine/status/(?P<claim_key>\w+)$', 'pair_status', name="vm_ajax_status"),
    url(r'^api/pair$', 'pair'),
    url(r'^api/cloud$', 'context_cloud'),
    url(r'^api/confirm$', 'confirm')
)

urlpatterns += patterns('cvmo.context.views.user',
    url(r'^login$', 'login',                        name="login"),
    url(r'^login_action', 'login_action',           name="do_login"),
    url(r'^register$', 'register',                  name="register"),
    url(r'^register_action$', 'register_action',    name="do_register"),
    url(r'^logout$', 'logout',                      name="logout"),
    url(r'^profile$', 'profile_edit',               name="profile"),
    url(r'^profile_save$', 'profile_edit_action',   name="profile_save"),
    url(r'^account_activation$', 'account_activation', name="account_activation")
)

urlpatterns += patterns('',
    # Examples:
    # url(r'^$', 'cvmo.views.home', name='home'),
    # url(r'^cvmo/', include('cvmo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
)

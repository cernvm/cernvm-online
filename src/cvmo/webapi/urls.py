from django.conf.urls import patterns, url

urlpatterns = patterns(
    "cvmo.webapi.views",
    url(r"^vmcp$",                       "vmcp",         name="webapi_vmcp"),
    url(r"^start/(?P<tag_id>[-\w]+)$",   "webstart_run", name="webapi_webstart_run"),
    url(r"^start$",                      "webstart_init",name="webapi_webstart_init"),
)

from django.conf.urls import patterns, url

urlpatterns = patterns(
    "cvmo.webapi.views",
    url(r"^vmcp$", 	"vmcp",         	name="webapi_vmcp"),
    url(r"^run",	"webstart_run", 	name="webapi_webstart_run"),
    url(r"^req$",	"webstart_req", 	name="webapi_webstart_req"),
)

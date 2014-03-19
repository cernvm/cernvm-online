from django.conf.urls import patterns, url

urlpatterns = patterns(
    "cvmo.core.views",
    url(r"^$", "show_welcome", name="core_welcome"),
)

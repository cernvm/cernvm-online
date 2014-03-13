from django.conf.urls import patterns, url

urlpatterns = patterns(
    "cvmo.dashboard.views",
    url(r"$", "dashboard", name="dashboard"),
)

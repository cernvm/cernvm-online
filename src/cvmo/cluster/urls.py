from django.conf.urls import patterns, url

urlpatterns = patterns(
    "cvmo.cluster.views",
    url(r"$", "show_cluster_new", name="cluster_new"),
)

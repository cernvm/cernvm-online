from django.conf.urls import patterns, url

urlpatterns = patterns(
    "cvmo.cluster.views",
    # Views
    url(r"^new$", "show_new", name="cluster_new"),
    url(r"^test$", "show_test"),
    # url(r"^edit/(?P<cluster_id>[0-9]+)$", "show_edit", name="cluster_edit"),
    # url(r"^deploy/(?P<cluster_id>[0-9]+)$", "show_deploy", name="cluster_deploy"),

    # Actions
    url(r"^save$", "save", name="cluster_save"),
    # url(r"^delete/(?P<cluster_id>[0-9]+)$", "delete", name="cluster_delete"),
)

from django.conf.urls import patterns, url

urlpatterns = patterns(
    "cvmo.market.views",
    url(r"^/revoke/(?P<context_id>[-\w]+)$", "revoke",
        name="market_revoke"),
    url(r"^/publish/(?P<context_id>[-\w]+)$", "publish",
        name="market_publish"),
    url(r"^/publish.do$", "publish_action",
        name="market_publish_action"),
    url(r"^/list$", "list", name="market_list"),
    url(r"^/list.search$", "list_ajax", name="market_list_search"),
    url(r"^/vote.do$", "vote_ajax", name="market_vote")
)

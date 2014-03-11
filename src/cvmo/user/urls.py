from django.conf.urls import patterns, url
from cvmo import settings

urlpatterns = patterns(
    "cvmo.user.views",

    #
    # Login, Logout
    #

    url(r"login$", "login", name="user_login"),
    url(r"login_action", "login_action", name="user_do_login"),
    url(r"logout$", "logout", name="user_logout"),

    #
    # Registration
    #

    url(r"register$", "register", name="user_register"),
    url(r"register_action$", "register_action",
        name="user_do_register"),
    url(r"account_activation$", "account_activation",
        name="user_account_activation"),

    #
    # Profile management
    #

    url(r"profile$", "profile_edit", name="user_profile"),
    url(r"profile_save$", "profile_edit_action",
        name="user_profile_save"),

    #
    # Bulk addition
    #

    url(r"bulk$", "bulk_add", name="user_bulk_add"),
    url(r"bulkcommit$", "bulk_add_commit",
        name="user_bulk_add_commit")
)

# Optional 2) CSC Login
if settings.ENABLE_CSC:
    urlpatterns += patterns(
        "cvmo.user.views",
        url(r"csc$", "csc_login", name="user_csc_login"),
        url(r"csc/login_action$", "csc_do_login",
            name="user_csc_do_login")
    )

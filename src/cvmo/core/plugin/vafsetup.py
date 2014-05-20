from cvmo.core.plugins import ContextPlugin

class VAFSetup(ContextPlugin):

    TITLE           = "Virtual Analysis Facility"
    DESCRIPTION     = "Configure the authentication method and the experiment settings for using the CernVM Virtual Analysis Facility"
    TEMPLATE        = "plugins/context-vafsetup.html"
    REMOVE_BLANK    = True

    # This is the internal name
    CONFIG_GROUP    = "vaf_setup"

    # This is the [section] name in the rendered context
    # (defaults to CONFIG_GROUP if not defined).
    CONFIG_GROUP_RENDERED = "vaf-setup"

    CONFIG_VARS     = {
        'node_type' : '',
        'auth_method': '',
        'client_settings': '',
        'alice_storage': ''
    }

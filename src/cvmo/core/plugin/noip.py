from cvmo.core.plugins import ContextPlugin

class NoIP(ContextPlugin):

    TITLE           = "NoIP"
    DESCRIPTION     = "register IP address with NOIP dynamic DNS service. Publishes ip at https://%(username)s:%(password)s@dynupdate.no-ip.com or, derive hostname from template <prefix><AMILaunchIndex+start>.<domain> "
    TEMPLATE        = "plugins/context-noip.html"
    REMOVE_BLANK    = True

    CONFIG_GROUP    = "noip"
    CONFIG_VARS     = {
            'username'  : '',
            'password'  : '',
            'hostname'  : '',
            'prefix'    : '',
            'domain'    : '',
            'start'     : 'no'
        }

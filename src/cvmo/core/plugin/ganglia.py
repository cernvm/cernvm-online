from cvmo.core.plugins import ContextPlugin

class Ganglia(ContextPlugin):

    TITLE           = "Ganglia"
    DESCRIPTION     = "Ganglia monitoring system"
    TEMPLATE        = "plugins/context-ganglia.html"
    REMOVE_BLANK    = True

    CONFIG_GROUP    = "ganglia"
    CONFIG_VARS     = {
            'name'                   : '',
            'owner'                  : '',
            'latlong'                : '',
            'url'                    : '',
            'location'               : ''
        }

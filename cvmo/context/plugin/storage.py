from cvmo.context.plugins import ContextPlugin

class Storage(ContextPlugin):
    
    TITLE           = "EC2 Storage"
    DESCRIPTION     = "Ephemeral EC2 storage configuration"
    TEMPLATE        = "plugins/context-storage.html"
    
    CONFIG_GROUP    = "storage"
    CONFIG_VARS     = {
            'daemon'                 : False,
            'pre-allocated-space'    : 20,
            'relocate-paths'         : '/srv/rmake-builddir:/srv/mysql'
        }

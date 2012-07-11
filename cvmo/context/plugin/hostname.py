from cvmo.context.plugins import ContextPlugin

class Hostname(ContextPlugin):
    
    TITLE           = "Custom Hostname"
    DESCRIPTION     = "Set a custom hostname on your Virtual Machine"
    TEMPLATE        = "plugins/context-hostname.html"
    
    CONFIG_GROUP    = "hostname"
    CONFIG_VARS     = {
            'hostname'  : ''
        }

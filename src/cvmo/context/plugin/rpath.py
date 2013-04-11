from cvmo.context.plugins import ContextPlugin

class rPath(ContextPlugin):
    
    TITLE           = "rPath Customizations"
    DESCRIPTION     = "Setup custom password for rAA or custom conary proxy"
    TEMPLATE        = "plugins/context-rpath.html"
    
    CONFIG_GROUP    = "rpath"
    CONFIG_VARS     = {
            'rap-password': '',
            'conaryproxy': ''
        }

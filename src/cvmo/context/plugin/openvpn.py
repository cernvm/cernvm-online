from cvmo.context.plugins import ContextPlugin
import base64

class OpenVPN(ContextPlugin):
    
    TITLE           = "OpenVPN"
    DESCRIPTION     = "Setup OpenVPN connection"
    TEMPLATE        = "plugins/context-openvpn.html"
    REMOVE_BLANK    = True
    
    CONFIG_GROUP    = "openvpn"
    CONFIG_VARS     = {
            'server'                 : '',
            'port'                   : '1194',
            'proto'                  : 'udp',
            'ca'                     : '',
            'key'                    : '',
            'cert'                   : '',
            'search'                 : '',
            'nameserver'             : '',
        }

    # Override the renderContextVariable to base64-encode the certificate contents
    def renderContextVariable(self, variable, value):
        encoded = ( 'ca', 'key', 'cert' )
        if (variable in encoded):
            return "%s=%s\n" % (variable,  base64.b64encode(str(value)))
        elif (variable in self.CONFIG_VARS):
            return "%s=%s\n" % (variable,  str(value))
        else:
            return False

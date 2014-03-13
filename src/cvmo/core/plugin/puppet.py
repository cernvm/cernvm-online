from cvmo.core.plugins import ContextPlugin
import re

class Puppet(ContextPlugin):

    TITLE           = "Puppet"
    DESCRIPTION     = "Start a puppet server or manage this vm by another puppet master"
    TEMPLATE        = "plugins/context-puppet.html"
    REMOVE_BLANK    = True

    CONFIG_GROUP    = "puppet"
    CONFIG_VARS     = {
            'puppet_server'          : '',
            'puppet_port'            : '8140',
            'puppet_log'             : '/var/log/puppet/puppet.log',
            'puppet_extra_opts'      : '--waitforcert=500',
            'puppetmaster_log'       : 'syslog',
            'puppetmaster_ports'     : '8140',
            'puppetmaster_extra_opts': '--no-ca',

            'mode'                   : 'slave',
        }

    def renderContext(self, values):
        """
        Validate values
        """

        # Remove puppet variables if we are running as master
        if (values['mode'] == 'master'):
            values['puppet_server'] = ""
            values['puppet_port'] = ""
            values['puppet_log'] = ""
            values['puppet_extra_opts'] = ""

            # Format ports in an array
            if 'puppetmaster_ports' in values:
                values['puppetmaster_ports'] = re.split("[ ,]+", values['puppetmaster_ports'])

        # Otherwise remove the puppetmaster variables
        else:
            values['puppetmaster_log'] = ""
            values['puppetmaster_ports'] = ""
            values['puppetmaster_extra_opts'] = ""

        # Do whatever my superclass does
        return ContextPlugin.renderContext( self, values )

    def renderContextVariable(self, variable, value):
        """
        Final transformations on the variables
        """
        if (variable == 'mode'):
            return False
        elif (variable == 'puppetmaster_ports'):
            return "%s=(%s)\n" % (variable,  " ".join(value))
        elif (variable in self.CONFIG_VARS):
            return "%s=%s\n" % (variable,  str(value))
        else:
            return False

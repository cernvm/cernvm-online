from cvmo.context.plugins import ContextPlugin

class Condor(ContextPlugin):
    
    TITLE           = "Condor Batch"
    DESCRIPTION     = "Setup Condor batch system"
    TEMPLATE        = "plugins/context-condor.html"
    REMOVE_BLANK    = True
    
    CONFIG_GROUP    = "condor"
    CONFIG_VARS     = {
            'condor_master' : '',
            'condor_secret' : '',
            'collector_name': '',
            'condor_user'   : 'condor',
            'condor_group'  : 'condor',
            'condor_dir'    : '',
            'condor_admin'  : '',
            'use_ips'       : 'false',
            'uid_domain'    : '*',
            'lowport'       : '41000',
            'highport'      : '42000'
        }

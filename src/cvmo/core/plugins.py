import base64
from django.conf import settings
from django.template import RequestContext, loader
from cvmo.core.utils.context import sanitize_env, sanitize
from cvmo.settings import CVMFS_UCVM_SERVERS, CVMFS_UCVM_DEFAULT_SERVER

#
#
# Contextualization plugin base class
#
#


class ContextPlugin(object):

    """ The base class to create context plugins """

    # Defaults
    TEMPLATE = "base/blank.html"
    TITLE = "Untitled context plugin"
    DESCRIPTION = ""
    CONFIG_GROUP = "undefined"
    CONFIG_GROUP_RENDERED = None
    CONFIG_VARS = {}
    REMOVE_BLANK = False

    def render(self, request, values):
        """ Render the module template into a string """

        # Simulate the nested values dictionary
        # because we also used it in the field names
        _values = {
            'values': {
                self.CONFIG_GROUP: self.validate_values(values)
            }
        }
        # print "Rendering to %s: " % self.CONFIG_GROUP, _values
        print "Doing %s" % self.TEMPLATE

        # First render the plugin body
        t = loader.get_template(self.TEMPLATE)
        return t.render(RequestContext(request, _values))

    def renderContextVariable(self, variable, value):
        """ An overridable function that returns the line to put on the
            contextualization script for the specified variable.
            It should return a string in 'key=value' format or False if
            you want to completely ignore this variable. """

        if (variable in self.CONFIG_VARS):
            return "%s=%s\n" % (variable,  str(value))
        else:
            return False

    def renderContext(self, values):
        """ Render the context variables into a text string (AMIConfig-compatible) """

        secname = self.CONFIG_GROUP_RENDERED
        if secname is None:
            secname = self.CONFIG_GROUP

        ans = "\n[%s]\n" % (secname)
        for k in self.CONFIG_VARS.keys():

            # Calculate template-safe key
            safeK = self.get_template_safe_key(k)

            # Check for a value in values
            _val = self.CONFIG_VARS[k]
            print ">> Looking for %s (safe of %s) in %s" % (safeK, k, str(values))
            if safeK in values:
                _val = values[safeK]

            # Render the variable
            if (_val != "") or not self.REMOVE_BLANK:
                v = self.renderContextVariable(k, _val)
                if (v != False):
                    ans += v

        return ans + "\n"

    def get_template_safe_key(self, key):
        """ Translate the key into something that can be safely used as template name (ex. '-' -> '_' ) """

        # Replace dashes
        safeK = key.replace("-", "_")

        # Return the new key
        return safeK

    def validate_values(self, values):
        """ Return a validated dictionary based on the values that were passed """

        # Check for missing keys
        for k in self.CONFIG_VARS.keys():

            # Calculate template-safe key
            safeK = self.get_template_safe_key(k)

            # Convert unsafe values
            if (k in values) and not (safeK in values):
                values[safeK] = values[k]
                del values[k]

            # Place missing values
            if not safeK in values:
                values[safeK] = self.CONFIG_VARS[k]

        # Return values
        return values

#
#
# Contextualization plugin database
#
#


class ContextPlugins(object):

    """ Operations on all of the context plugins """

    def __get_class(self, cls):
        """ Fetch a class definition from the specified string """
        parts = cls.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    def get_names(self):
        """ Return the class names of all the plugins """
        return self.plugins.keys()

    def get(self, name):
        """ Return the class instance of the spcified plugin """
        return self.plugins[name]

    def renderAll(self, request, values, enabled=None):
        """ Render all the plugins """
        if enabled == None:
            enabled = {}

        _ans = []
        for k in self.plugins.keys():
            _p = self.plugins[k]

            # Extract the plugin variables
            _values = {}
            if _p.CONFIG_GROUP in values:
                _values = values[_p.CONFIG_GROUP]

            # Check if this is enabled
            is_enabled = False
            if k in enabled:
                if enabled[k]:
                    is_enabled = True

            # Render/place in dictionary
            _ans.append({
                'body': _p.render(request, _values),
                'title': _p.TITLE,
                'description': _p.DESCRIPTION,
                'id': k,
                'enabled': is_enabled
            })

        return _ans

    def renderCoreContext(self, values, enable_plugins):
        """ Render the very basic, hard-coded stuff """

        # Ensure enable_plugins is prefixed with ' '
        if enable_plugins != "":
            enable_plugins = " " + enable_plugins

        # Check if we should enable the raa plugin
        _cvm_wa_ctx = ""
        if 'cvm_wa_password' in values['general']:
            # for CernVM 2.x
            enable_plugins = " rapadminpassword" + enable_plugins
            _cvm_wa_ctx = "\n[rpath]\n"
            _cvm_wa_ctx += "rap-password=%s\n" % values[
                'general']['cvm_wa_password']
            # for CernVM 3.x
            enable_plugins = " cernvm_appliance" + enable_plugins
            _cvm_wa_ctx += "\n[cernvm_appliance]\n"
            _cvm_wa_ctx += "password=%s\n" % values[
                'general']['cvm_wa_password']

        # If we have startup script put it here now
        _ans = ""
        if ('startup_script' in values['general']) and (values['general']['startup_script']):
            _ans += "#!/bin/sh\n"
            _ans += ". /etc/cernvm/site.conf\n"
            _ans += str(values['general']['startup_script']).replace("\r", "")
            _ans += "exit\n"

        # Prepare amiconfig header
        _ans += "[amiconfig]\n"
        _ans += "plugins=cernvm%s\n" % enable_plugins

        # Push CernVM Web appliance context config
        if _cvm_wa_ctx != "":
            _ans += _cvm_wa_ctx

        # Prepare some general stuff for CernVM
        _ans += "\n[cernvm]\n"
        _ans += "organisations=%s\n" % values['general']['organisation']
        _ans += "repositories=%s\n" % values['general']['repositories']
        _ans += "shell=%s\n" % values['general']['shell']
        _ans += "config_url=%s\n" % values['general']['config_url']

        # EOS (TODO: not optimal, work in progress)
        v = values['general'].get('eos_server')
        if v is not None and v != '':
            _ans += 'eos-server=%s\n' % v
        v = values['general'].get('x509_user')
        if v is not None and v != '':
            _ans += 'x509-user=%s\n' % v
        v = values['general'].get('x509_cert')
        if v is not None and v != '':
            _ans += 'x509-cert=%s\n' % base64.b64encode( v )

        # Prepare contextualization_command
        if ('context_cmd' in values['general']) and (values['general']['context_cmd'] != ''):
            if 'context_cmd_user' in values['general']:
                _ans += "contextualization_command=%s:%s\n" % (
                    values['general']['context_cmd_user'], values['general']['context_cmd'])

        # Prepare services
        if 'services' in values['general']:
            _svcs = values['general']['services']
            if 'custom_services' in values['general']:
                if (_svcs != ''):
                    _svcs += ','
                _svcs += values['general']['custom_services']
            if _svcs != "":
                _ans += "services=%s\n" % _svcs

        # Are we on uCernVM?
        if 'cvm_version' in values['general'] and values['general']['cvm_version'] == 'uCernVM':
            is_ucernvm = True
        else:
            is_ucernvm = False

        # Prepare users string
        _userstr = ""
        if 'users' in values['general']:
            for user in values['general']['users'].values():
                if _userstr != "":
                    _userstr += ","
                _userstr += user['name'] + ":" + user[
                    'group'] + ":" + str(user['password'])
            _ans += "users=%s\n" % _userstr

        # Prepare proxy
        if values['general']['http_proxy_mode'] == 'auto':
            _proxy = None
        else:
            if values['general']['http_proxy_mode'] == 'direct':
                _proxy = "DIRECT"
            else:
                _proxy = values['general']['http_proxy_mode'] + "://"

                # Check if we should add a user
                if ('http_usecredentials' in values['general']) and (values['general']['http_usecredentials']):
                    _proxy += values['general']['http_username'] + ":"
                    _proxy += str(values['general']['http_password']) + "@"

                # Set hostname/port
                _proxy += values['general']['http_proxy'] + ":"
                _proxy += str(values['general']['http_proxy_port'])

                # Check for fallback
                if ('http_fallback' in values['general']) and (values['general']['http_fallback']):
                    _proxy += ";DIRECT"

            _ans += "proxy=%s\n" % _proxy

        # Setup environment
        if 'environment' in values['general']:
            _env = ""
            for k in values['general']['environment'].keys():
                v = sanitize_env(values['general']['environment'][k])
                if _env != "":
                    _env += ","
                _env += "%s=%s" % (k, v)
            _ans += "environment=%s\n" % _env

        # Setup CernVM-Edition
        if 'cvm_edition' in values['general']:
            _ans += "edition=%s\n" % values['general']['cvm_edition']

            # If we have desktop, setup X and resolution
            if values['general']['cvm_edition'] == 'Desktop':

                # Setup resolution
                if 'cvm_resolution' in values['general']:
                    _ans += "screenRes=%s\n" % values[
                        'general']['cvm_resolution']
                if 'cvm_keyboard_layout' in values['general']:
                    _ans += "keyboard=%s\n" % values[
                        'general']['cvm_keyboard_layout']
                if 'cvm_startx' in values['general']:
                    if (values['general']['cvm_startx'] == 1):
                        _ans += "startXDM=on\n"
                    else:
                        _ans += "startXDM=off\n"

        if is_ucernvm:

            # Setup uCernVM specific section
            _ucvm = ''
            if _proxy is not None:
                _ucvm += "cvmfs_http_proxy=\"%s\"\n" % _proxy
            if 'resize_rootfs' in values['general'] and values['general']['resize_rootfs'] == 'true':
                _ucvm += "resize_rootfs=true\n"

            if 'cvmfs_branch' in values['general'] and values['general']['cvmfs_branch'] != '':
                _ucvm += "cvmfs_branch=%s\n" % values['general']['cvmfs_branch']

                # Where do we get this branch from?
                try:
                    cvm_server = CVMFS_UCVM_SERVERS[ values['general']['cvmfs_branch'] ]
                    if cvm_server != CVMFS_UCVM_DEFAULT_SERVER:
                        # don't write useless defaults
                        _ucvm += 'cvmfs_server=%s\n' % (cvm_server)
                except KeyError:
                    # ignore if not found
                    pass

            if 'cvmfs_tag' in values['general'] and values['general']['cvmfs_tag'] != '' and values['general']['cvmfs_tag'] != 'trunk':
                _ucvm += "cvmfs_tag=%s\n" % values['general']['cvmfs_tag']
            if _ucvm != '':
                # Write only if necessary
                _ans += "\n[ucernvm-begin]\n%s[ucernvm-end]\n" % _ucvm

        return _ans

    def renderContext(self, uuid, values, enabled):
        """ Render all the enabled plugins into a string """

        # If enabled is nothing, make empty array
        if not enabled:
            enabled = []

        # Find the group names of the enabled plugins
        _plugins = ""
        for k in self.plugins.keys():
            if (k in enabled) and (enabled[k]):
                if _plugins != "":
                    _plugins += " "
                if self.plugins[k].CONFIG_GROUP_RENDERED is not None:
                    _plugins += self.plugins[k].CONFIG_GROUP_RENDERED
                else:
                    _plugins += self.plugins[k].CONFIG_GROUP

        # Prepare context
        if enabled == None:
            enabled = {}
        _ans = self.renderCoreContext(values, _plugins)

        # Process keys
        for k in self.plugins.keys():
            _p = self.plugins[k]

            # Skip disabled plugins
            if not k in enabled:
                continue
            if not enabled[k]:
                continue

            # Extract the plugin values
            _values = {}
            if _p.CONFIG_GROUP in values:
                _values = values[_p.CONFIG_GROUP]

            # Extract the plugin variables
            _ans += _p.renderContext(_values)

        # Start by placing some identification information
        _script = "VM_CONTEXT_UUID=%s\n" % uuid
        _script += 'VM_CONTEXT_NAME="%s"\n' % sanitize(values['name'])

        # Then build the contextualization script
        _script += "EC2_USER_DATA=%s\n" % base64.b64encode(_ans)

        # If we have a private key, add it too
        if ('root_ssh_key' in values) and (values['root_ssh_key'] != ""):
            _script += "ROOT_PUBKEY=%s\n" % base64.b64encode(
                sanitize(values['root_ssh_key']))

        # Return script
        return _script

    def __init__(self):
        """ Initialize the context plugins store """
        self.plugins = {}

        # Register all the plugins defined in CONTEXT_PLUGINS
        for clsname in settings.CONTEXT_PLUGINS:
            _class = self.__get_class(clsname)
            _inst = _class()
            self.plugins[clsname] = _inst

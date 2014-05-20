import json
import pickle
import copy
import base64
import crypt
import urllib2
import re
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from cvmo.core.plugins import ContextPlugins
from cvmo.context.models import ContextDefinition
from querystring_parser import parser
from cvmo.core.utils.context import gen_context_key, tou, salt_context_key
from cvmo.core.utils.views import get_list_allowed_abstract, uncache_response, \
    render_password_prompt


def blank_abstract(request):
    global _generic_plugin

    p_names = ContextPlugins().get_names()
    p_dict = []

    p_dict.append(_generic_plugin)

    # A default html_body value for convenience
    abstract = {
        "html_body": """
<table class="plain long-text">
    <tr>
        <th width="150">Multiple choices:</th>
        <td>
            <select name="values[custom][multiple]">
                <option value="choice#1">1st choice</option>
                <option value="choice#2">2nd choice</option>
            </select>
        </td>
    </tr>
    <tr>
        <th width="150">Input text:</th>
        <td><input name="values[custom][text]" value="any text value"/></td>
    </tr>
</table>
"""
    }

    for p_n in p_names:
        p = ContextPlugins().get(p_n)
        p_dict.append({"title": p.TITLE, "name": p_n})

    # Render the response
    return render(
        request,
        "context/abstract.html",
        {
            "plugins": p_dict,
            "abstract": abstract
        }
    )


def create_abstract(request):
    post_dict = parser.parse(
        unicode(request.POST.urlencode()).encode("utf-8"))

    # We are interested in values, enabled and abstract. Let"s insert empty
    # values in case some of them are null (values and abstract are never null)
    if post_dict.get("enabled") == None:
        post_dict["enabled"] = {}

    # There is no specific model for the abstract context, so we will just use
    # the ContextDefinition model. Since this context is abstract, no rendered
    # version will be saved in ContextStorage
    c_uuid = gen_context_key()
    c_data = pickle.dumps({
        "values": post_dict["values"],
        "enabled": post_dict["enabled"],
        "abstract": post_dict["abstract"]
    })

    # For debug
    # return uncache_response(HttpResponse(json.dumps(post_dict, indent=2), \
    #     content_type="text/plain"))

    ContextDefinition.objects.create(
        id=c_uuid,
        name=tou(post_dict["values"]["name"]),
        description=u"",  # TODO
        owner=request.user,
        key=u"",
        public=False,  # TODO
        data=c_data,
        checksum=0,  # TODO
        inherited=False,
        abstract=True
    )

    return redirect("dashboard")


def clone_abstract(request, context_id):
    global _generic_plugin

    item = ContextDefinition.objects.get(id=context_id)
    data = pickle.loads(str(item.data))
    display = data["abstract"].get("display")

    p_names = ContextPlugins().get_names()
    p_dict = []

    # Display CernVM generic plugin? (It is always enabled anyway)
    generic_plugin_cp = copy.deepcopy(_generic_plugin)
    if display == None:
        generic_plugin_cp["display"] = False
    else:
        generic_plugin_cp["display"] = \
            (display.get(_generic_plugin["name"]) == 1)

    p_dict.append(generic_plugin_cp)

    for p_n in p_names:
        p = ContextPlugins().get(p_n)
        p_e = (data["enabled"].get(p_n) == 1)
        if display != None:
            p_d = (display.get(p_n) == 1)
        else:
            p_d = False
        p_dict.append({"title": p.TITLE, "name": p_n,
                       "enabled": p_e, "display": p_d})

    data["values"]["name"] = _name_increment_revision(
        tou(data["values"]["name"])
    )

    return render(
        request,
        "context/abstract.html",
        {
            "values": data["values"],
            "abstract": data["abstract"],
            "enabled": data["enabled"],
            "plugins": p_dict
        }
    )


def context_from_abstract(request, context_id, cloning=False):
    """
    Used both when creating a simple context and when cloning it
    """
    global _generic_plugin

    item = ContextDefinition.objects.get(id=context_id)

    # Check if the data are encrypted
    if item.key == "":
        data = pickle.loads(str(item.data))
    else:
        # Password-protected
        resp = _prompt_unencrypt_context(
            request, item,
            reverse("context_clone_simple", kwargs={"context_id": context_id})
        )
        if "httpresp" in resp:
            return resp["httpresp"]
        elif "data" in resp:
            data = pickle.loads(resp["data"])

    display = data["abstract"].get("display")

    # Render all of the plugins
    plugins = ContextPlugins().renderAll(request, data["values"],
                                         data["enabled"])

    # Append display property to every plugin. Defaults to False
    for p in plugins:
        if display == None:
            p["display"] = False  # default
        else:
            p["display"] = (display.get(p["id"]) == 1)

    # Display CernVM generic plugin? (It is always enabled anyway)
    generic_plugin_cp = copy.deepcopy(_generic_plugin)
    if display == None:
        generic_plugin_cp["display"] = False
    else:
        generic_plugin_cp["display"] = (
            display.get(_generic_plugin["name"]) == 1)

    # Change original name
    if cloning:
        data["values"]["name"] = _name_increment_revision(
            tou(data["values"]["name"])
        )
    else:
        data["values"]["name"] = "Context from " + data["values"]["name"]

    # Render the response
    # raw = {"data": data}  # debug
    return render(
        request,
        "context/context.html",
        {
            "cernvm": _get_cernvm_config(),
            "values": data["values"],
            "json_values": json.dumps(data["values"]),
            "disabled": False,
            "id": "",
            "parent_id": context_id,
            #"raw": json.dumps(raw, indent=2),
            "abstract_html": data["abstract"].get("html_body"),
            "from_abstract": True,
            "plugins": plugins,  # now each plugin will hold enable=True|False
            "cernvm_plugin": generic_plugin_cp
        }
    )

# Gets the list of abstract contexts with the following fields:
#   id, name, public
# Users will get a list of the "shown" ones only plus their own. If
# is_abstract_creation_enabled == True, the full list is obtained.


def ajax_abstract_list(request):
    ab_list = get_list_allowed_abstract(request)
    ab_dict = []
    for ab in ab_list:
        ab_dict.append({
            "id": ab.id,
            "name": ab.name,
            "public": ab.public
        })
    return uncache_response(
        HttpResponse(
            json.dumps(ab_dict, indent=2), content_type="application/json"
        )
    )

#
# Helpers
#

# String corresponding to the generic plugin name
_generic_plugin = {
    "title": "Basic CernVM configuration",
    "name": "generic_cernvm",
    "display": True,
    "enabled": True
}


def _get_cernvm_config():
    """ Download the latest configuration parameters from CernVM """

    try:
        response = urllib2.urlopen("http://cernvm.cern.ch/config/")
        _config = response.read()

        # Parse response
        _params = {}
        _config = _config.split("\n")
        for line in _config:
            if line:
                (k, v) = line.split("=", 1)
                _params[k] = v

        # Generate JSON map for the CERNVM_REPOSITORY_MAP
        _cvmMap = {}
        _map = _params["CERNVM_REPOSITORY_MAP"].split(",")
        for m in _map:
            (name, _optlist) = m.split(":", 1)
            options = _optlist.split("+")
            _cvmMap[name] = options

        # Update CERNVM_REPOSITORY_MAP
        _params["CERNVM_REPOSITORY_MAP"] = json.dumps(_cvmMap)
        _params["CERNVM_ORGANISATION_LIST"] = _params[
            "CERNVM_ORGANISATION_LIST"].split(",")

        # Return parameters
        return _params

    except Exception as ex:
        print "Got error: %s\n" % str(ex)
        return {}


def _prompt_unencrypt_context(request, ctx, callback_url, decode_data=True,
                              decode_render=False):
    """
    Takes care of prompting user for a password and returning an unencrypted
    version of a given context "data" section and "rendered" representation.
    Decoded data is returned as strings. No "unpickling" is performed
    """
    resp = {}
    title = "Context encrypted"
    body = "The context information you are trying to use are encrypted with " \
        "a private key. Please enter such key below to decrypt:"

    if "password" in request.POST:
        # POST already contains "unicode" data!
        pwd = request.POST["password"].encode("ascii", "ignore")
        if salt_context_key(ctx.id, pwd) == ctx.key:
            # Password is OK: decrypt
            if decode_data:
                resp["data"] = crypt.decrypt(
                    base64.b64decode(str(ctx.data)), pwd)
            if decode_render:
                render = ContextStorage.objects.get(id=ctx.id)
                m = re.search(r"^ENCRYPTED:(.*)$", render.data)
                if m:
                    resp["render"] = crypt.decrypt(
                        base64.b64decode(str(m.group(1))), pwd)
                # Response empty in case of problems
        else:
            # Password is wrong
            resp["httpresp"] = render_password_prompt(
                request, title, body, callback_url,
                {"msg_error": "Wrong password"}
            )
    else:
        # Prompt for password
        resp["httpresp"] = render_password_prompt(request, title, body,
                                                  callback_url)

    return resp


def _name_increment_revision(name):
    """
    If the given (context) name ends with a number, returns the same name with
    that number incremeted by one. In case it doesn"t, appends a "(copy)" at the
    end of the given name.
    """
    revre = r"^(.*?)([0-9]+)$"
    m = re.search(revre, name)
    if m:
        name = m.group(1) + str(int(m.group(2)) + 1)
    else:
        name = name + " (copy)"
    return name

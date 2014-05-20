from cvmo.context.models import ContextDefinition
from django.shortcuts import render, redirect
from django.db.models.query_utils import Q


def set_memory(request, var="", data=""):

    # No variable defined, update the whole entry
    if data == "":
        request.session["global__memory"] = var
        return

    # Update particular entry
    if not "global__memory" in request.session:
        request.session["global__memory"] = {}


def get_memory(request, var="", default=""):

    # Memory not available, get default
    if not "global__memory" in request.session:
        return default

    # Var not specified, get entire memory
    if var == "":
        return request.session["global__memory"]

    # Var not exists, get default
    if not var in request.session["global__memory"]:
        return default

    # Return variable
    return request.session["global__memory"][var]


def redirect_memory(url, request):
    """
    Store the request in memory (that can be obtained with get_memory) and
    return a redirect directive.
    """

    # Get data
    if request.method == "POST":
        request.session["global__memory"] = request.POST.dict()
    elif request.method == "GET":
        request.session["global__memory"] = request.GET.dict()

    # Redirect
    return redirect(url)


def msg_display(request, kind, message):
    """
    Display a global message
    """
    if not "global__" + kind in request.session:
        request.session["global__" + kind] = ""
    else:
        request.session["global__" + kind] += "<br />"
    request.session["global__" + kind] += message


def msg_error(request, message):
    msg_display(request, "error", message)


def msg_warning(request, message):
    msg_display(request, "warning", message)


def msg_confirm(request, message):
    msg_display(request, "confirm", message)


def msg_info(request, message):
    msg_display(request, "info", message)


def uncache_response(response):
    """
    Disable caching on the response
    """

    # Expired in the past
    response["Expires"] = "Tue, 03 Jul 2001 06:00:00 GMT"

    # Do not cache
    response[
        "Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"

    # Return uncached stuff
    return response


def render_password_prompt(request, title, message, url_ok, extras={}):
    """
    Render the password prompt screen
    """
    variables = extras
    variables["title"] = title
    variables["message"] = message
    variables["url_ok"] = url_ok
    return render(
        request, "base/password.html", variables
    )


def render_confirm(request, title, message, url_ok, url_cancel, extras={}):
    """
    Render the confirmation dialog
    """
    variables = extras
    variables["action"] = title
    variables["message"] = message
    variables["url_ok"] = url_ok
    variables["url_cancel"] = url_cancel
    return render(
        request, "base/confirm.html", variables
    )


def is_abstract_creation_enabled(request):
    """
    Check if the current user can create abstract contexts
    """
    if request.user:
        return request.user.groups.filter(name="abstract").count() != 0
    return False

# Returns a list of displayable abstract contexts for the currently enabled set
# of options (such as current user and other settings)


def get_list_allowed_abstract(request):
    if is_abstract_creation_enabled(request):
        # Administrator: get all abstract contexts
        ab_list = ContextDefinition.objects.filter(
            Q(inherited=False) & Q(abstract=True)).order_by("name")
    else:
        # Normal user: get only own contexts plus public ones
        ab_list = ContextDefinition.objects.filter(
            Q(inherited=False) & Q(abstract=True) & (
                Q(owner=request.user) | Q(public=True)
            )).order_by("name")
    return ab_list

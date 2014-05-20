from django.db.models.query_utils import Q
import cvmo
from cvmo import settings
from cvmo.context.models import ContextDefinition
from cvmo.core.utils.views import is_abstract_creation_enabled

def version(request):
    """
    Adds the version number in the template.
    """
    return {
        "cvmo_version": cvmo.__version__
    }

def custom_messages(request):
    """
    Custom handler to append messages in the context.
    TODO: Must be removed and replaced with Django messages
    """

    # Pop global messages from the session
    msg_error = ""
    if "global__error" in request.session:
        msg_error = request.session["global__error"]
        del request.session["global__error"]
    msg_warning = ""
    if "global__warning" in request.session:
        msg_warning = request.session["global__warning"]
        del request.session["global__warning"]
    msg_confirm = ""
    if "global__confirm" in request.session:
        msg_confirm = request.session["global__confirm"]
        del request.session["global__confirm"]
    msg_info = ""
    if "global__info" in request.session:
        msg_info = request.session["global__info"]
        del request.session["global__info"]

    # Prepare custom context
    ans = {
        "msg_error": msg_error,
        "msg_warning": msg_warning,
        "msg_confirm": msg_confirm,
        "msg_info": msg_info,
    }

    # Delete memory
    if "global__memory" in request.session:
        del request.session["global__memory"]

    return ans


def sidebar(request):
    ans = {}
    if request.user.is_authenticated():
        ans["ip_address"] = request.META["REMOTE_ADDR"]
        ans["last_context_definitions"] = ContextDefinition.objects.filter(
            Q(Q(owner=request.user) | Q(public=True))
            & Q(inherited=False)
            & Q(abstract=False)
        ).order_by("-id")[:5]
    return ans


def flags(request):
    """
    TODO: Abstract contexts to be removed
    """
    ans = {
        "enable_csc": settings.ENABLE_CSC,
        "enable_abstract_creation": is_abstract_creation_enabled(request)
    }
    return ans

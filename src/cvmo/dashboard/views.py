from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q
from cvmo import settings
from cvmo.vm.models import Machines
from cvmo.context.models import ContextDefinition
from cvmo.cluster.models import ClusterDefinition
from cvmo.core.utils.views import uncache_response
from cvmo.core.utils.views import get_list_allowed_abstract


def dashboard(request):
    context = {
        "context_definition_list": ContextDefinition.objects.filter(
            Q(owner=request.user) & Q(inherited=False) & Q(abstract=False)
        ).order_by("-public", "name"),

        "full_abstract_list": get_list_allowed_abstract(request),
        "my_abstract_list": ContextDefinition.objects.filter(
            Q(owner=request.user) & Q(inherited=False) & Q(abstract=True)
        ).order_by("name"),

        "cluster_definition_list": ClusterDefinition.objects.filter(
            owner=request.user
        ).order_by("name"),

        "machine_list": Machines.objects.filter(owner=request.user)
    }
    context["webapi_configurations"] = settings.WEBAPI_CONFIGURATIONS
    push_to_context("redirect_msg_info", "msg_info", context, request)
    push_to_context("redirect_msg_error", "msg_error", context, request)
    push_to_context("redirect_msg_warning", "msg_warning", context, request)
    push_to_context("redirect_msg_confirm", "msg_confirm", context, request)

    return uncache_response(
        render_to_response(
            "dashboard/dashboard.html", context, RequestContext(request)
        )
    )

def push_to_context(sessionName, contextName, context, request):
    if sessionName in request.session:
        context[contextName] = request.session[sessionName]
        del request.session[sessionName]

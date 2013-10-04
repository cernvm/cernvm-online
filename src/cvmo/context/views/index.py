from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q

from cvmo import settings

from cvmo.context.models import ContextDefinition, Machines, ClusterDefinition, MarketplaceContextEntry

from cvmo.context.plugins import ContextPlugins
from cvmo.context.utils.views import uncache_response

from cvmo.context.utils.views import get_list_allowed_abstract

def welcome(request):
    return render_to_response('pages/welcome.html', {}, RequestContext(request))

def dashboard(request):
    context = {
        'context_list': ContextDefinition.objects.filter(Q(owner=request.user) & Q(inherited=False) & Q(abstract=False)).order_by('-public', 'name'),
	'context_list_reverse': ContextDefinition.objects.filter(Q(owner=request.user) & Q(inherited=False) & Q(abstract=False)).order_by('-public', '-name'),
        'full_abstract_list': get_list_allowed_abstract(request),
        'my_abstract_list': ContextDefinition.objects.filter(Q(owner=request.user) & Q(inherited=False) & Q(abstract=True)).order_by('name'),
        'cluster_list': ClusterDefinition.objects.filter(owner=request.user).order_by('-public', 'name'),
        'machine_list': Machines.objects.filter(owner=request.user)
    }
    if settings.ENABLE_WEBAPI:
        context["webapi_configurations"] = settings.WEBAPI_CONFIGURATIONS
    push_to_context("redirect_msg_info", "msg_info", context, request)
    push_to_context("redirect_msg_error", "msg_error", context, request)
    push_to_context("redirect_msg_warning", "msg_warning", context, request)
    push_to_context("redirect_msg_confirm", "msg_confirm", context, request)

    return uncache_response(render_to_response('pages/dashboard.html', context, RequestContext(request)))

def test(request):
    raw = "<h1>404 - Not found</h1><p>This is not the website you are looking for</p>"
    return render_to_response('core/raw.html', {'body': raw}, RequestContext(request))

def push_to_context(sessionName, contextName, context, request):
    if sessionName in request.session:
        context[contextName] = request.session[sessionName]
        del request.session[sessionName]

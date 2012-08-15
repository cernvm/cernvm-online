from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q

from cvmo.context.models import ContextDefinition, Machines, ClusterDefinition

from cvmo.context.plugins import ContextPlugins
from cvmo.context.utils.views import uncache_response

def welcome(request):
    return render_to_response('pages/welcome.html', {}, RequestContext(request))

def dashboard(request):
    context = {
        'context_list': ContextDefinition.objects.filter(Q(owner=request.user) & Q(inherited=False)),
        'cluster_list': ClusterDefinition.objects.filter(owner=request.user),
        'machine_list': Machines.objects.filter(owner=request.user),
    }
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

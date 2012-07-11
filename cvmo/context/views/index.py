from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from cvmo.context.models import ContextDefinition, Machines
#from cvmo.context.models import ClusterDefinition

from cvmo.context.plugins import ContextPlugins
from cvmo.context.utils.views import uncache_response

def welcome(request):
    return render_to_response('pages/welcome.html', {}, RequestContext(request))

def dashboard(request):
    return uncache_response(render_to_response('pages/dashboard.html', {
            'context_list': ContextDefinition.objects.filter(owner=request.user),
            'cluster_list': [], #ClusterDefinition.objects.filter(owner__username="user")
            'machine_list': Machines.objects.filter(owner=request.user),
        }, RequestContext(request)))

def test(request):
    raw = "<h1>404 - Not found</h1><p>This is not the website you are looking for</p>"
    return render_to_response('core/raw.html', {'body': raw}, RequestContext(request))

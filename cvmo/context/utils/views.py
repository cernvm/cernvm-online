from cvmo.context.models import ContextDefinition, ClusterDefinition
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.db.models.query_utils import Q

def global_context(request):
    
    # Do nothing if we have no user
    if not request.user.is_authenticated():
        return {}
    
    # Read user-specific information
    return {
        'ip_address': request.META['REMOTE_ADDR'],
        'last_context_definitions': ContextDefinition.objects.filter(Q(Q(owner=request.user) | Q(public=True)) & Q(inherited=False)).order_by('-id')[:5],
        'last_cluster_definitions': ClusterDefinition.objects.filter(Q(owner=request.user) | Q(public=True)).order_by('-id')[:5]
    }

def uncache_response(response):

    # Expired in the past
    response['Expires'] = 'Tue, 03 Jul 2001 06:00:00 GMT"'

    # Do not cache
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'

    # Return uncached stuff
    return response

def render_password_prompt(request, title, message, url_ok, extras={}):
    variables = extras
    variables['title'] = title
    variables['message'] = message
    variables['url_ok'] = url_ok
    return render_to_response('core/password.html', variables, RequestContext(request))
    
def render_confirm(request, title, message, url_ok, url_cancel, extras={}):
    variables = extras
    variables['action'] = title
    variables['message'] = message
    variables['url_ok'] = url_ok
    variables['url_cancel'] = url_cancel
    return render_to_response('core/confirm.html', variables, RequestContext(request))

def render_error(request, title, message, url_redir):
    variables = extras
    variables['title'] = title
    variables['body'] = message
    variables['url_redir'] = url_redir
    return render_to_response('core/error.html', variables, RequestContext(request))

def render_error(request, code=400, title="", body=""):

    def_titles = {
            400: 'Invalid Request',
            401: 'Unauthorized',
            402: 'Payment Required',
            403: 'Forbidden',
            404: 'Not Found',
            405: 'Method Not Allowed',
            406: 'Not Acceptable',
            407: 'Proxy Authentication Required',
            408: 'Request Timeout',
            409: 'Conflict',
            410: 'Gone',
            411: 'Length Required',
            412: 'Precondition Failed',
            413: 'Request Entity Too Large',
            414: 'Request-URI Too Long',
            415: 'Unsupported Media Type',
            416: 'Requested Range Not Satisfiable',
            417: 'Expectation Failed',
            500: 'Internal error',
            501: 'Not Implemented',
            502: 'Bad Gateway',
            503: 'Service Unavailable',
            504: 'Gateway Timeout',
            505: 'HTTP Version Not Supported'
        }
    
    # Guess the title if it's missing
    if title == "":
        title = def_titles.get(code, "")

    # Put default body if missing
    if body == "":
        body = 'Your browser sent a request that the server cannot process. <br />This either means you are not authorized, your request was mailformed or there was an internal error. <br />Make sure your request is correct and try again later.'

    # Render the error page
    t = loader.get_template('core/error.html')
    _html = t.render(RequestContext(request, { 'body': body, 'code': code, 'title': title }))
    
    # Return the error page
    return HttpResponse(_html, status=code)
    
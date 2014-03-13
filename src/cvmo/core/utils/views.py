from cvmo.context.models import ContextDefinition
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.conf import settings
from django.db.models.query_utils import Q


def global_context(request):
    """
    Custom handler to append additional
    """

    # Pop global messages from the session
    msg_error = ""
    if 'global__error' in request.session:
        msg_error = request.session['global__error']
        del request.session['global__error']
    msg_warning = ""
    if 'global__warning' in request.session:
        msg_warning = request.session['global__warning']
        del request.session['global__warning']
    msg_confirm = ""
    if 'global__confirm' in request.session:
        msg_confirm = request.session['global__confirm']
        del request.session['global__confirm']
    msg_info = ""
    if 'global__info' in request.session:
        msg_info = request.session['global__info']
        del request.session['global__info']

    # Prepare custom context
    ans = {
        'msg_error': msg_error,
        'msg_warning': msg_warning,
        'msg_confirm': msg_confirm,
        'msg_info': msg_info,
        'enable_cloud': settings.ENABLE_CLOUD and is_cloud_enabled(request),
        'enable_csc': settings.ENABLE_CSC,
        'enable_abstract_creation': is_abstract_creation_enabled(request)
    }

    # Append some extra info if we are authenticated
    if request.user.is_authenticated():
        ans['ip_address'] = request.META['REMOTE_ADDR']
        ans['last_context_definitions'] = ContextDefinition.objects.filter(
            Q(Q(owner=request.user) | Q(public=True))
            & Q(inherited=False)
            & Q(abstract=False)
        ).order_by('-id')[:5]
        # ans['last_cluster_definitions'] = ClusterDefinition.objects.filter(
        #     Q(owner=request.user) | Q(public=True)).order_by('-id')[:5]

    # Delete memory
    if 'global__memory' in request.session:
        del request.session['global__memory']

    # Return resulting context
    return ans


def set_memory(request, var='', data=''):

    # No variable defined, update the whole entry
    if data == '':
        request.session['global__memory'] = var
        return

    # Update particular entry
    if not 'global__memory' in request.session:
        request.session['global__memory'] = {}


def get_memory(request, var='', default=''):

    # Memory not available, get default
    if not 'global__memory' in request.session:
        return default

    # Var not specified, get entire memory
    if var == '':
        return request.session['global__memory']

    # Var not exists, get default
    if not var in request.session['global__memory']:
        return default

    # Return variable
    return request.session['global__memory'][var]


def redirect_memory(url, request):
    """
    Store the request in memory (that can be obtained with get_memory) and
    return a redirect directive.
    """

    # Get data
    if request.method == 'POST':
        request.session['global__memory'] = request.POST.dict()
    elif request.method == 'GET':
        request.session['global__memory'] = request.GET.dict()

    # Redirect
    return redirect(url)


def msg_display(request, kind, message):
    """
    Display a global message
    """
    if not 'global__' + kind in request.session:
        request.session['global__' + kind] = ""
    else:
        request.session['global__' + kind] += "<br />"
    request.session['global__' + kind] += message


def msg_error(request, message):
    msg_display(request, 'error', message)


def msg_warning(request, message):
    msg_display(request, 'warning', message)


def msg_confirm(request, message):
    msg_display(request, 'confirm', message)


def msg_info(request, message):
    msg_display(request, 'info', message)


def uncache_response(response):
    """
    Disable caching on the response
    """

    # Expired in the past
    response['Expires'] = 'Tue, 03 Jul 2001 06:00:00 GMT"'

    # Do not cache
    response[
        'Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'

    # Return uncached stuff
    return response


def render_password_prompt(request, title, message, url_ok, extras={}):
    """
    Render the password prompt screen
    """
    variables = extras
    variables['title'] = title
    variables['message'] = message
    variables['url_ok'] = url_ok
    return render_to_response(
        'base/password.html', variables, RequestContext(request)
    )


def render_confirm(request, title, message, url_ok, url_cancel, extras={}):
    """
    Render the confirmation dialog
    """
    variables = extras
    variables['action'] = title
    variables['message'] = message
    variables['url_ok'] = url_ok
    variables['url_cancel'] = url_cancel
    return render_to_response(
        'base/confirm.html', variables, RequestContext(request)
    )


def render_error(request, title, message, url_redir):
    """
    Render a full screen-error with an optional URL redirection after some time
    """
    variables = extras
    variables['title'] = title
    variables['body'] = message
    variables['url_redir'] = url_redir
    return render_to_response(
        'base/error.html', variables, RequestContext(request)
    )


def render_error(request, code=400, title="", body=""):
    """
    Render an error page
    """
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
        body = 'Your browser sent a request that the server cannot process.\
 <br />This either means you are not authorized, your request was mailformed\
 or there was an internal error. <br />Make sure your request is correct and\
 try again later.'

    # Render the error page
    t = loader.get_template('base/error.html')
    _html = t.render(
        RequestContext(request, {'body': body, 'code': code, 'title': title}))

    # Return the error page
    return HttpResponse(_html, status=code)


def is_cloud_enabled(request):
    """
    Check if the current user has cloud permissions
    """
    if request.user:
        return request.user.groups.filter(name='cloud').count() != 0
    return False


def is_abstract_creation_enabled(request):
    """
    Check if the current user can create abstract contexts
    """
    if request.user:
        return request.user.groups.filter(name='abstract').count() != 0
    return False

# Returns a list of displayable abstract contexts for the currently enabled set
# of options (such as current user and other settings)


def get_list_allowed_abstract(request):
    if is_abstract_creation_enabled(request):
        # Administrator: get all abstract contexts
        ab_list = ContextDefinition.objects.filter(
            Q(inherited=False) & Q(abstract=True)).order_by('name')
    else:
        # Normal user: get only own contexts plus public ones
        ab_list = ContextDefinition.objects.filter(
            Q(inherited=False) & Q(abstract=True) & (
                Q(owner=request.user) | Q(public=True)
            )).order_by('name')
    return ab_list


def for_cloud(fn):
    """
    Decorator to reject access if the user is not member of the cloud group
    """
    def wrapped(*args, **kwargs):

        # Fetch request object
        request = args[0]

        # Check if user is not member of cloud
        if not is_cloud_enabled(request):
            msg_info(
                request, "This is an experimental feature. Access is granted\
 only to beta testers!")
            return redirect('dashboard')

        # It looks OK, run the view
        return fn(*args, **kwargs)

    # Return the wrapped function
    return wrapped


def for_market(fn):
    """
    Decorator to reject access if the user is not member of the market group
    """
    def wrapped(*args, **kwargs):

        # Fetch request object
        # request = args[0]

        # It looks OK, run the view
        return fn(*args, **kwargs)

    # Return the wrapped function
    return wrapped

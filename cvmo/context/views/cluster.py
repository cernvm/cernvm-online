import urllib2
import json
import pickle
import uuid
import hashlib
import base64

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.hashers import make_password, check_password

from cvmo.context.plugins import ContextPlugins
from cvmo.context.models import ContextStorage, ContextDefinition
from cvmo.querystring_parser import parser

from cvmo.context.utils.views import render_confirm, render_password_prompt
from cvmo.context.utils import crypt

def api_get(request, cluster_id):
    pass

def blank(request):
    return render_to_response('pages/cluster.html', {
        "values": {
            "instances": [ ]
        },
        "disabled": False
    }, RequestContext(request))

def context_get_key(name):
    ctx = ContextDefinition.objects.get(name=name)
    return ctx.key

def create(request):
    post_dict = parser.parse(request.POST.urlencode())
    msg_warning = ""
    
    # Skip the indexing keys, get only the values as array
    if 'instances' in post_dict['values']:
        post_dict['values']['instances'] = post_dict['values']['instances'].values()

        # Generate warnings:
        # 1) If we used a context with a key, ensure that all the contexts
        #    have the same key
        key_used=""
        for o in post_dict['values']['instances']:
            k=context_get_key(o['context'])
            if k!='':
                msg_warning+='<p>You are using encrypted context definitions in your cluster. To avoid problems, please make sure that they are all encrypted with the same secret!</p>'
                break

    return render_to_response('pages/cluster.html', {
        "values" : post_dict['values'],
        "disabled": False,
        "msg_info": str(post_dict),
        "msg_warning": msg_warning
    }, RequestContext(request))

def clone(request, cluster_id):
    pass

def view(request, cluster_id):
    pass

def delete(request, cluster_id):
    pass

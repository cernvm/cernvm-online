"""
Shibboleth SSO Authentication and ADFS User Synchronization Middleware

This middleware checks the HTTP headers for Shibboleth/ADFS headers in order to
detect a successful previous authentication via shibboleth SSO. 

This middleware is configured and tuned by a required dictionary in the settings.py:

SHIBBOLETH_SSO = {

    # Header bindings
    'login_header': 'HTTP_ADFS_LOGIN',
    'groups_header': 'HTTP_ADFS_GROUP',
    'fullname_header': 'HTTP_ADFS_FULLNAME',
    'email_header': 'HTTP_ADFS_EMAIL',
    
    # Groups to add to the user, depending on groups_header
    'map_groups': {
        'admin': r'(;|^)cernvm-infrastructure(;|$)'
    },
    
    # Which regex on groups_header should mark the user as staff (login on admin page)
    'staff_groups': [
        r'(;|^)cernvm-infrastructure(;|$)'
    ],
    
    # Where to redirect if the user is not authenticated
    # (Can be relative or absolute URL)
    'redirect_login': '/admin/',
    
    # Which website paths are publicly accessible and will not
    # trigger the redirect
    'public_path': [
        r'/admin/$',
        r'/api/context/?$',
        r'/api/pair/?$',
        r'/api/confirm/?$',
        r'/api/cloud/?$'
    ]
}

"""
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.conf import settings

from django.template import RequestContext, loader
from django.http import HttpResponse
from django.shortcuts import redirect

import logging
import re

def setup_permissions(user, request, config):
        
    # Fetch header
    groups = request.META[config['groups_header']]
    
    # Setup staff
    user.is_staff = False
    user.is_superuser = False
    if 'staff_groups' in config:
        for rx in config['staff_groups']:
            p = re.compile(rx)
            if p.search(groups):
                user.is_staff = True
                user.is_superuser = True
                break
    
    # Setup groups
    # (TODO: Implement)

class ShibbolethUserSync(object):  
    """ Synchronize database and authenticate user if shibboleth and ADFS headers
        are detected in an HTTP request. """
    def process_request(self, request):
        # Get a logger
        logger = logging.getLogger(__name__)
        
        # Fetch shibboleth configuration
        config = {}
        try:
            # If SHIBBOLETH_SSO is missing, trap the exception
            config = settings.SHIBBOLETH_SSO
        except AttributeError:
            # Not found
            logger.error('Missing SHIBBOLETH_SSO configuration in settings.py!')
            return None
        
        # If we are authenticated, do nothing
        if not request.user.is_authenticated():

            # Check if we have shibboleth headers
            if (config['login_header'] in request.META) and (request.META[config['login_header']] != ''):
                
                # Fetch login and group info
                loginname = request.META[config['login_header']]
            
                # Check if the user exists in the database.
                # Otherwise create it...
                try:
                    u = User.objects.get(username=loginname)
                except:
                    u = User(username=loginname)

                # Extract username
                if ('fullname_header' in config):
                    fullname = request.META[config['fullname_header']]
                    parts = fullname.split(" ",1)
                    if len(parts) > 1:
                        u.first_name = parts[0]
                        u.last_name = parts[1]
                    else:
                        u.first_name = parts[0]
                
                # Extract email
                if ('email_header' in config):
                    u.email = request.META[config['email_header']]

                # Setup permissions
                setup_permissions(u,request,config)
                u.save()

                # Login user
                try:
                    u.backend='django.contrib.auth.backends.ModelBackend'
                    login(request, u)
                except Exception as ex:
                    print "Exception %s" % str(ex)
            
            # Nope? Deny access...
            else:
                
                # Check for allowed URLs
                if 'public_path' in config:
                    for url in config['public_path']:
                        p = re.compile(url)
                        if p.match(request.path):
                            return None
                
                # Otherwise redirect
                return redirect(config['redirect_login'])
        
        # No shibboleth found/user authenticated
        return None

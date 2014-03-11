import ConfigParser
import crypt
from ConfigParser import NoOptionError
from django.template.context import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.models import User
from django.conf import settings
from cvmo.context.utils.views import msg_error, uncache_response
from django.contrib.auth import login as django_login


def csc_login(request):
    """ Display screen """
    if request.user is not None and request.user.is_authenticated():
        return redirect("dashboard")

    return uncache_response(
        render_to_response("user/login_csc.html", {}, RequestContext(request))
    )


def csc_do_login(request):
    """ Login """
    if request.user is not None and request.user.is_authenticated():
        return redirect("dashboard")

    u_name = request.POST.get('username', '')
    if u_name == '':
        msg_error(request, "Please specify a username!")
        return redirect("user_csc_login")

    u_pwd = request.POST.get('password', '')
    if u_pwd == '':
        msg_error(request, "Please specify a password!")
        return redirect("user_csc_login")

    # Open config file
    config = ConfigParser.RawConfigParser()
    config.read(settings.CSC_USER_CONFIG_FILE)

    # Read user parameter
    try:

        # Fetch the salted password
        salted_pwd = config.get('accounts', u_name)
        if not salted_pwd:
            msg_error(request, "Invalid username/password combination!")
            return redirect("user_csc_login")

        # Validate password
        if crypt.crypt(u_pwd, salted_pwd) != salted_pwd:
            msg_error(request, "Invalid username/password combination!")
            return redirect("user_csc_login")

        # Calculate the loginname
        u_loginname = "csc_" + u_name

        # Check if the user exists in the database.
        # Otherwise create it...
        try:
            u = User.objects.get(username=u_loginname)
        except:

            # Create new user
            u = User(username=u_loginname)

            # Setup permissions
            u.set_password(u_pwd)
            u.save()

        # Login user
        try:
            u.backend = 'django.contrib.auth.backends.ModelBackend'
            django_login(request, u)
        except Exception as ex:
            msg_error(request, "An error occured! " + str(ex))
            return redirect("user_csc_login")

    except NoOptionError:
        msg_error(request, "Invalid username/password combination!")
        return redirect("user_csc_login")

    except Exception as e:
        msg_error(request, "An error occured! " + str(e))
        return redirect("user_csc_login")

    # Everything was ok, the user is logged in
    return redirect("dashboard")

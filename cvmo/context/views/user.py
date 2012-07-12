from django.http import HttpResponse
from django.template.context import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib import auth
from django.contrib.auth.models import User
import re

def login(request):
    if user_is_logged(request):
        return redirect("dashboard")
    
    # Get form error
    if "login_error" in request.session:
        context = { "msg_error": request.session["login_error"] }
        del request.session["login_error"]
    else:
        context = {}
        
    return render_to_response("pages/login.html", context, RequestContext(request))

def login_action(request):
    if user_is_logged(request):
        return redirect("dashboard")
    
    # Parse request
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    if username == '' or password == '':
        request.session["login_error"] = "Plase fill in username and password!"
        return redirect("login")
    
    # Try login user
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_authenticated():
        auth.login(request, user)
        return redirect("dashboard")
    else:
        # Failed to login user
        request.session["login_error"] = "Invalid combination of user name and password!"
        return redirect("login")

def register(request):
    if user_is_logged(request):
        return redirect("dashboard")
    
    # Get form error
    if "form_error" in request.session:
        context = { "msg_error": request.session["form_error"] }
        del request.session["form_error"]
    else:
        context = {}
    
    # Reproduce form
    if "form" in request.session:
        context["user"] = request.session["form"]
        del request.session["form"]
    
    return render_to_response("pages/profile.html", context, RequestContext(request))

def register_action(request):
    """
        TODO LIST: 
            1) Email validation
            2) Send email to activate account(?)
            3) CAPTACHA field(?)
    """
    if user_is_logged(request):
        return redirect("dashboard")    
    
    # Parse request
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    retypePassword = request.POST.get('retype_password', '')
    email = request.POST.get('email', '')
    firstName = request.POST.get('first_name', '')
    lastName = request.POST.get('last_name', '')
    form = {
        "username": username,
        "email": email,
        "first_name": firstName,
        "last_name": lastName
    }    
    
    # Required fields filled?
    if username == '' or password == '' or retypePassword == '' or email == '':
        request.session["form_error"] = "Please fill in all required fields!"
        request.session["form"] = form
        return redirect("register")
    
    # Check if email is valid
    if not is_valid_email(email):
        request.session["form_error"] = "Please provide a valid email address"
        request.session["form"] = form
        return redirect("register")
    
    # Are password the same?
    if password != retypePassword:
        request.session["form_error"] = "Passwords are not the same"
        request.session["form"] = form
        return redirect("register")
    
    # Is username used?
    try:
        user = User.objects.get(username=username)
        request.session["form_error"] = "User with user name %s already exists." % username
        request.session["form"] = form
        return redirect("register")
    except:
        pass
      
    # Is email used?
    try:
        user = User.objects.get(email=email)
        request.session["form_error"] = "User with email address %s already exists." % email
        request.session["form"] = form
        return redirect("register")
    except:
        pass    
    
    # Create user
    user = User(username=username,email=email)
    user.set_password(password)
    user.first_name = firstName
    user.last_name = lastName
    try:
        user.save()
    except:
        request.session["form_error"] = "Failed to store new user!"
        request.session["form"] = form
        return redirect("register")
    
    # Login user and proceed
    loggedUser = auth.authenticate(username=username, password=password)
    auth.login(request, loggedUser)
    
    request.session["redirect_msg_info"] = "Your account has been created!"
    return redirect("dashboard")

def logout(request):
    if not user_is_logged(request):
        return redirect("login")

    # Check if this is a CERN SSO user
    sso_user=False
    if request.user.password == '':
        sso_user=True

    # Logout from Django (Important)
    auth.logout(request)
    
    # Check if the user if from cern 
    if sso_user:
        return redirect("https://login.cern.ch/adfs/ls/?wa=wsignout1.0")
    
    # Otherwise, go back to login
    return redirect("login")

def profile_edit(request):
    if not user_is_logged(request):
        return redirect("login")
    
    # Get form error
    if "form_error" in request.session:        
        context = { "msg_error": request.session["form_error"] }
        del request.session["form_error"]
    else:
        context = {}
    
    # Reproduce form
    if "form" in request.session:
        context["user"] = request.session["form"]
        del request.session["form"]
    else:
        context["user"] = request.user
        
    context["profile_edit"] = True
    
    return render_to_response("pages/profile.html", context, RequestContext(request))

def profile_edit_action(request):
    if not user_is_logged(request):
        return redirect("login")
    
    # Parse request
    currentPassword = request.POST.get("current_password", "")
    newPassword = request.POST.get('password', '')
    retypeNewPassword = request.POST.get('retype_password', '')
    email = request.POST.get('email', '')
    firstName = request.POST.get('first_name', '')
    lastName = request.POST.get('last_name', '')
    form = {
        "email": email,
        "first_name": firstName,
        "last_name": lastName
    }    
    
    # Required fields filled?
    if email == '':
        request.session["form_error"] = "Please fill in all required fields!"
        request.session["form"] = form
        return redirect("profile")     
    
    # Check if email is valid
    if not is_valid_email(email):
        request.session["form_error"] = "Please provide a valid email address"
        request.session["form"] = form
        return redirect("profile")
        
    # Change password
    if currentPassword != '':
        # Check old password
        if not request.user.check_password(currentPassword):
            request.session["form_error"] = "Old password is not corrent"
            request.session["form"] = form
            return redirect("profile")
        
        # Are new passwords the same?
        if newPassword != retypeNewPassword:
            request.session["form_error"] = "Passwords are not the same"
            request.session["form"] = form
            return redirect("profile")
            
    # Is email used?
    try:
        user = User.objects.get(email=email)
        # Ignore same user i.e. if email is unchanged
        if user.username != request.user.username:            
            request.session["form_error"] = "User with email address %s already exists." % email
            request.session["form"] = form
            return redirect("profile")
    except:
        pass    
    
    # Modify user
    request.user.first_name = firstName
    request.user.last_name = lastName
    request.user.email = email
    if newPassword != '':
        request.user.set_password(newPassword)
        
    # Store changes
    try:
        request.user.save()
    except:
        request.session["form_error"] = "Failed to store new user!"
        request.session["form"] = form
        return redirect("profile")
    
    request.session["redirect_msg_info"] = "Your account has been modified!"
    return redirect("dashboard")

"""
   Helper functions 
"""

def user_is_logged(request):
    return request.user is not None \
        and request.user.is_authenticated()

def is_valid_email(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return True
    return False

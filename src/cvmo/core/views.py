from django.shortcuts import render
from cvmo import settings

#
# Error handlers
#


def handle_error_400(request):
    context = {
        "admins": settings.ADMINS
    }
    return render(request, "base/error/400.html", context, status=400)


def handle_error_404(request):
    context = {
        "admin_email": settings.ADMINS[0][1]
    }
    return render(request, "base/error/404.html", context, status=404)


def handle_error_500(request):
    context = {
        "admins": settings.ADMINS
    }
    return render(request, "base/error/500.html", context, status=500)


#
# Welcome view
#


def show_welcome(request):
    return render(request, "core/welcome.html")

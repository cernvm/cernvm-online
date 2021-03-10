import os
import sys

# Modify the path
sys.path.append("/var/www/cernvm-online/lib/python2.7/site-packages")
sys.path.append("/var/www/cernvm-online/lib64/python2.7/site-packages")

# Run app
os.environ['DJANGO_SETTINGS_MODULE'] = "cvmo.settings"
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

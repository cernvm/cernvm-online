import os
import sys

# Modify the path
sys.path.insert(0, "/var/www/cernvm-online/lib64/python2.6/site-packages")
sys.path.insert(0, "/var/www/cernvm-online/lib/python2.6/site-packages")

# Run app
os.environ['DJANGO_SETTINGS_MODULE'] = "cvmo.settings"
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

#!/bin/bash
pip uninstall CernVM-Online
pip uninstall PIL PyCrypto Django django-cors-headers
pip uninstall mysql-python
yum remove python-devel gcc python-pip git mod_wsgi httpd mysql-devel -y
rm /var/www/cernvm-online -Rf

#!/bin/bash
echo -n "View at http://"
ifconfig eth1 | grep 'inet addr' | sed -r 's/.*?inet addr:([^ ]+).*/\1/'
python manage.py runserver 0.0.0.0:8000

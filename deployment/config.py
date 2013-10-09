#
# CernVM Online Configuration file
#

#
# General
#

# Debug mode?
DEBUG = False
# Managers
ADMINS = (("CernVM", "cernvm.administrator@cern.ch"))
# Allowed hosts, applicable when DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "cernvm-online.cern.ch", "cvmo.cern.ch"]
# Django secret key, please use a different key for each deployment
# Utility: http://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = "4mi)06bf^%)*rd(w6ua0#c4lz0*wufjy4nr6=qw+oiffl$cp"
# URL prefix
#   if CernVM online is deployed in https://cvmo.ch/example/ URL_PREFIX should
#   be set to 'example/'
URL_PREFIX = ""
# Enable the cloud interfaces?
ENABLE_CLOUD = True

#
# Paths
#

LOG_PATH =      "/var/www/cernvm-online/logs"
PUBLIC_PATH =   "/var/www/cernvm-online/public_html"

#
# Database
#

DB = {
    "backend":  "mysql",
    "host":     "dbod-cvmonl.cern.ch",
    "user":     "admin",
    "password": "oA@Yga51sE",
    "name":     "cvmo",
    "port":     5502
}

#
# User registration
#

GOOGLE_RECAPTCHA = {
    # Get from https://www.google.com/recaptcha/admin/create
    "public_key": "6LdG6tMSAAAAAMDBse8Dzze0Wz_3WGTwfUdyz60Z",
    "private_key": "6LdG6tMSAAAAAJTx1HqU69b-r90tERI51U8Gn-F2"
}

ACTIVATION_EMAIL = {
    "sender": "CernVM Online",
    "sender_email": "cernvm.administrator@cern.ch",
    "subject": "Account activation"
}

#
# CORS Whitelist
#

CORS_ORIGIN_REGEX_WHITELIST = ("^http?://(\w+\.)?cern\.ch$")

#
# WebAPI configurations
#

WEBAPI_CONFIGURATIONS = [
    {
        "cpus": 1, "memory": 1024, "disk_size": 10000,
        "label": "1 CPU / 1 GB RAM / 10 GB disk"
    },
    {
        "cpus": 1, "memory": 2048, "disk_size": 10000,
        "label": "1 CPU / 2 GB RAM / 10 GB disk"
    },
    {
        "cpus": 2, "memory": 2048, "disk_size": 20000,
        "label": "2 CPU / 2 GB RAM / 20 GB disk"
    }
]

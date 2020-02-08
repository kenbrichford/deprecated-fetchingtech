import os

from .base import *

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False
ALLOWED_HOSTS = ['.fetchingtech.com', '.pythonanywhere.com']

# secure redirect
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# sendgrid
SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']

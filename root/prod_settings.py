import os
from .settings import *

DEBUG = False

INTERNAL_IPS = [
    "127.0.0.1",
    "0.0.0.0"
]

CSRF_TRUSTED_ORIGINS = [
        "https://ritzin.dev"
        ]

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = [
    "web"
]

DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': os.environ.get("POSTGRES_DB"),
                'USER': os.environ.get("POSTGRES_USER"),
                'PASSWORD': os.environ.get("POSTGRES_PASSWORD"),
                'HOST': os.environ.get("POSTGRES_HOST"),
                'PORT': os.environ.get("POSTGRES_PORT"),
            }
        }
ADMINS = [("Ava Wallenfang", "ava@wallenfang.de")]

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = "/var/log/django/app-messages"

EMAIL_BACKEND = 'gmailapi_backend.mail.GmailBackend'
GMAIL_API_CLIENT_ID = os.environ["GMAIL_API_CLIENT_ID"]
GMAIL_API_CLIENT_SECRET = os.environ["GMAIL_API_CLIENT_SECRET"]
GMAIL_API_REFRESH_TOKEN = os.environ["GMAIL_API_REFRESH_TOKEN"]


#EMAIL_HOST = os.environ["EMAIL_HOST"]
#EMAIL_PORT = os.environ["EMAIL_PORT"]
#EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
#EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
#EMAIL_USE_TLS = os.environ["EMAIL_USE_TLS"]


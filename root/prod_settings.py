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

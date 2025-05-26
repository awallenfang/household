import os
from .settings import *

DEBUG = False

CSRF_TRUSTED_ORIGINS = [
        "https://ritzin.dev"
        ]

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = [
    "web"
]
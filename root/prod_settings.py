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

ADMINS = [("Ava Wallenfang", "ava@wallenfang.de")]

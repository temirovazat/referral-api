import os

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')


CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = [
    "http://127.0.0.1",
    "http://localhost",
]

CORS_ALLOW_CREDENTIALS = True

"""Database."""

import os
from types import MappingProxyType

DATABASES = MappingProxyType(
    {
        'default': {
            'ENGINE': os.getenv('DB_ENGINE', default='django.db.backends.postgresql'),
            'NAME': os.getenv('DB_NAME', default='postgres'),
            'USER': os.getenv('DB_USER', default='postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', default='postgres'),
            'HOST': os.getenv('DB_HOST', default='localhost'),
            'PORT': os.getenv('DB_PORT', default='5432')
        }
    },
)

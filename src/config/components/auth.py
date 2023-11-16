"""Authentication settings."""

import os
from datetime import timedelta

AUTH_USER_MODEL = 'users.User'

AUTH_CODE_EXPIRES_MINUTES = int(os.getenv('AUTH_CODE_EXPIRES_MINUTES', default=10))

REFRESH_TOKEN_LIFETIME_DAYS = int(os.getenv('REFRESH_TOKEN_LIFETIME_DAYS'))

ACCESS_TOKEN_LIFETIME_MINUTES = int(os.getenv('ACCESS_TOKEN_LIFETIME_MINUTES'))

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'TOKEN_OBTAIN_SERIALIZER': 'api.v1.users.serializers.CustomTokenObtainSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'api.v1.users.serializers.CustomTokenRefreshSerializer',
}

"""Authentication settings."""

import os

AUTH_USER_MODEL = 'users.User'

AUTH_CODE_EXPIRES_MINUTES = os.getenv('AUTH_CODE_EXPIRES_MINUTES', default=10)

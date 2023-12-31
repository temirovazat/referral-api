import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', get_random_secret_key())

DEBUG = os.environ.get('DEBUG', False) == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

include(
    'components/application_definition.py',
    'components/api.py',
    'components/http.py',
    'components/database.py',
    'components/password_validation.py',
    'components/internationalization.py',
    'components/static_files.py',
    'components/auth.py',
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

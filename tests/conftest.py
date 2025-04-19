import os
import sys
import django
import pytest
from pathlib import Path


# Determine the root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent

# Add the project directory and the Django project directory to the sys.path
sys.path.insert(0, str(ROOT_DIR))  # Root directory of the project
sys.path.insert(0, str(ROOT_DIR / 'example'))  # Django project directory

# Set the default Django settings module for the 'example' project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')


@pytest.fixture(scope='session', autouse=True)
def django_setup():
    django.setup()

#!/usr/bin/env python

import sys
import django

from django.conf import settings
from django.core.management import call_command

settings.configure(
    DEBUG=True,
    INSTALLED_APPS=(
        'django.contrib.contenttypes',
        'np_autodiscovery',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.humanize',
        'cacheops',
        'corsheaders',
        'debug_toolbar',
        'django_filters',
        'django_tables2',
        'django_prometheus',
        'mptt',
        'rest_framework',
        'taggit',
        'taggit_serializer',
        'timezone_field',
        'circuits',
        'dcim',
        'ipam',
        'extras',
        'secrets',
        'tenancy',
        'users',
        'utilities',
        'virtualization',
        'drf_yasg',
    ),
    WEBHOOKS_ENABLED=False,
    BASE_PATH='',
)

django.setup()
call_command('makemigrations', 'np_autodiscovery')

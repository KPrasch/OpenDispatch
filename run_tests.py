#! python

import os, sys
from twisted.scripts.trial import run as run_tests

# begin chdir armor
sys.path[:] = map(os.path.abspath, sys.path)
# end chdir armor

sys.path.insert(0, os.path.abspath(os.getcwd()))
sys.argv.append("apps/map/tests.py")


####
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def run_django_settings():
    from django.conf import settings
    settings.configure(
        MIDDLEWARE_CLASSES=[],
        ROOT_URLCONF='dispatch.urls',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'apps.collect',
            'apps.map',
            'apps.people',
            'apps.weather'
            ],
        SECRET_KEY="LLAMAS",

        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            }
        },
        ALLOWED_HOSTS="*",
        DEBUG=True,
    )
    import django
    django.setup()

run_django_settings()
run_tests()
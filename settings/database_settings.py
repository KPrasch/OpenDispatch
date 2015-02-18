DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dispatch_db_dev',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    },
     'postgis': {
         'ENGINE': 'django.contrib.gis.db.backends.postgis',
         'NAME': 'geodjango',
         'USER': 'geo',
     }
             }

class GisRouter(object):

    def db_for_read(self, model, **hints):

        if model._meta.app_label == 'map':
            return 'postgis'
        return None

    def db_for_write(self, model, **hints):

        if model._meta.app_label == 'auth':
            return 'postgis'
        return None

    def allow_relation(self, obj1, obj2, **hints):
 
        if obj1._meta.app_label == 'map' or \
           obj2._meta.app_label == 'map':
           return True
        return None

    def allow_migrate(self, db, model):

        if db == 'postgis':
            return model._meta.app_label == 'map'
        elif model._meta.app_label == 'map':
            return False
        return None

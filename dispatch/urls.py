from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

import apps.map.api
import apps.collect.incident
import apps.people.views


router = routers.DefaultRouter()
router.register(r'accounts', apps.people.views.AccountView, 'list')
router.register(r'incidents', apps.map.api.IncidentViewSet, 'list')
router.register(r'insights', apps.map.api.InsightViewSet, 'list')
admin.autodiscover()

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
    ]

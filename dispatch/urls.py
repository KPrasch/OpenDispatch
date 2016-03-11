from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

import apps.map.views
import apps.collect.views
import apps.people.views


router = routers.DefaultRouter()
router.register(r'accounts', apps.people.views.AccountView, 'list')
router.register(r'incidents', apps.map.views.IncidentViewSet, 'list')
router.register(r'insights', apps.map.views.InsightViewSet, 'list')
admin.autodiscover()

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^dispatches/$', apps.map.views.map_view),
    ]


'''
urlpatterns = [
    # Admin and Auth URLs
    url(r'^api/', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', apps.people.views.app_login),
    url(r'^accounts/logout/$', apps.people.views.logout),

    url(r'^dispatches/(?P<venue>.*)$', apps.map.views.map_view),
    url(r'^incidents/search/$', apps.collect.views.search_incidents),
    url(r'^incidents/filter/daterange/$', apps.collect.views.filter_incidents_daterange),
    url(r'^get_incidents/$', apps.map.views.get_incide),
    url(r'^get_geoincidents/$', apps.map.views.get_geoincidents),
    url(r'^get_geoincidents/(?P<venue>.*)$', apps.map.views.get_geoincidents),
    #url(r'^get_streetview/(?P<location_string>.*)/$', apps.map.views.get_streetview),
    url(r'^most_recent/$', apps.map.views.most_recent_dispatch),
]
'''
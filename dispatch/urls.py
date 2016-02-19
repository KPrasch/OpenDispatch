from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from apps.collect.views import stream_twitter
import apps.map.views
import apps.collect.views
import apps.public.views
import apps.people.views
import apps.public.views

admin.autodiscover()

urlpatterns = [
    # Admin and Auth URLs
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', apps.people.views.app_login),
    url(r'^accounts/logout/$', apps.people.views.logout),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^about/$', apps.public.views.about_view),
    url(r'^dispatches/$', apps.map.views.map_view),
    url(r'^dispatches/(?P<venue>.*)$', apps.map.views.map_view),
    url(r'^incidents/search/$', apps.collect.views.search_incidents),
    url(r'^graph/$', apps.map.views.bubble_view),
    url(r'^get_geoincidents/$', apps.map.views.get_geoincidents),
    url(r'^get_geoincidents/(?P<venue>.*)$', apps.map.views.get_geoincidents),
    #url(r'^get_streetview/(?P<location_string>.*)/$', apps.map.views.get_streetview),
    url(r'^most_recent/$', apps.map.views.most_recent_dispatch),
]

# Do once on Django startup. Is there a better place for this to live?
stream_twitter()
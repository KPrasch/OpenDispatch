from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dispatch_gmail.views.extract_gmail_dispatches', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^/login/$', 'django.contrib.auth.views.login',
                        {'template_name': 'plus/login.html'}),

    url(r'^admin/', include(admin.site.urls)),

    url('', include('social.apps.django_app.urls', namespace='social')),

    url(r'^download-gmail/', 'dispatch_gmail.views.extract_gmail_incidents', name='home'),
    url(r'^incidents/', 'dispatch_gmail.views.incident_table'),

    url(r'^$', 'dispatch_gmail.views.dashboard', name='dashboard'),


)

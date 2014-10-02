from django.conf.urls import patterns, include, url
from django.contrib import admin
from dispatch_gmail import views


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dispatch_gmail.views.extract_gmail_dispatches', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^/login/$', 'django.contrib.auth.views.login',
                        {'template_name': 'plus/login.html'}),

    url(r'^admin/', include(admin.site.urls)),

    url('', include('social.apps.django_app.urls', namespace='social')),

    url(r'^download-gmail/', 'dispatch_gmail.views.get_incident_emails', name='home'),
    url(r'^incidents/', 'dispatch_gmail.views.gross_hourly_most_common'),
    url(r'^parse/', 'dispatch_gmail.views.parse_incident_emails'),

    url(r'^$', 'dispatch_gmail.views.dashboard', name='dashboard'),


)

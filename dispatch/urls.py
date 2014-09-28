from django.conf.urls import patterns, include, url
from django.contrib import admin
from dispatch_gmail import views


admin.autodiscover()

urlpatterns = patterns('',

    # Examples:
    # url(r'^$', 'dispatch_gmail.views.extract_gmail_dispatches', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social_auth.urls')),


    url(r'^/login/$', 'django.contrib.auth.views.login',
                        {'template_name': 'plus/login.html'}),
    #url(r'^$', 'dispatch_gmail.views.dashboard', name='dashboard'),

    url(r'^download-gmail/', 'dispatch_gmail.views.get_incident_emails', name='home'),
    url(r'^extract_incidents/', 'dispatch_gmail.views.parse_incident_emails'),

)

from django.conf.urls import patterns, include, url
from django.contrib import admin
from dispatch_gmail import views
from dispatch_twitter import views

admin.autodiscover()

urlpatterns = patterns('',
                       
    #Django admin web interface
    url(r'^admin/', include(admin.site.urls)),
                       
    #Authentication                   
    url(r'^/login/$', 'django.contrib.auth.views.login',
                        {'template_name': 'plus/login.html'}),
    url('', include('social.apps.django_app.urls', namespace='social')),

    #Incident db population from gmail
    url(r'^import-email/', 'dispatch_gmail.views.import_email_incidents'),
    #url(r'^parse-gmail/', 'dispatch_gmail.views.parse_incident_emails'),
    
    #Incident db population from twitter
    url(r'^import-twitter/', 'dispatch_twitter.views.import_twitter_incidents'),
    #url(r'^parse-twitter/', 'dispatch_twitter.views.parse_twitter_incidents'),
    
    #Forward facing URLs
    url(r'^$', 'dispatch_gmail.views.dashboard', name='dashboard'),
    url(r'^incidents/', 'dispatch_gmail.views.gross_hourly_most_common'),

)

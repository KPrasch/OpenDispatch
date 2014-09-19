from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dispatch_gmail.views.extract_gmail_dispatches', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^all/', 'dispatch_gmail.views.extract_gmail_iar_incidents', name='home'),

    url(r'^admin/', include(admin.site.urls)),
)

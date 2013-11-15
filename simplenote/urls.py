from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic.simple import redirect_to

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'simplenote.views.home', name='home'),
    # url(r'^ghinote/', include('ghinote.foo.urls')),
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.urls')),
    url(r'^member/', include('simplenote.member_urls')),
    url(r'^feedback', 'simplenote.views.feedback', name='home'),
    url(r'^about', 'simplenote.views.about', name='About'),
    url(r'^guide', 'simplenote.views.guide', name='Guide'),
    url(r'^favicon\.ico/?$', redirect_to, {'url':'/static/img/favicon.ico'}),
)

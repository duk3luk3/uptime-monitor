from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'do_track_site.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^uptime/', include('uptime.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^$', RedirectView.as_view(pattern_name='uptime.index')),
)

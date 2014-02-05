from django.conf.urls import patterns, include, url

from django.http import HttpResponseRedirect

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sc_lims.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^lims/', include('lims.urls')),

    url(r'^$', lambda r: HttpResponseRedirect('lims/')),
    url(r'^lims/', include('lims.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

from django.conf.urls import patterns, url

from lims import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)

from __future__ import print_function

import sys

from django.conf.urls import patterns, url
from django.db.models import get_models
from django.template.defaultfilters import slugify

import lims
from lims import views


def default_model_views():
    urls = []

    # Create urls for all models in lims if they have a preffered_ordering
    # attribute
    for model in get_models(app_mod=lims.models):
        #print(model.__name__, file=sys.stderr)
        if hasattr(model, 'preferred_ordering'):
            urls += [url(r'^' + slugify(model.__name__) + r'/(\d)/$', views.default_object_table(model), name='lims.views.' + slugify(model.__name__))]
        urls += [url(r'^browse/%s$' % slugify(model.__name__), views.default_object_list(model), name='lims.views.browse.' + slugify(model.__name__))]

    return urls


urlpatterns = patterns(*['lims.views'] +
    default_model_views() +
    [
    url(r'^$', views.index, name='index'),
    url(r'^browse/$', views.browse, name='browse'),
    url(r'^tree/sample/(\d+)/$', views.sample_tree_json, name='sample_tree'),
    url(r'^barcode/$', views.barcode_index, name='barcode_index'),
    url(r'^barcode/(.*)/$', views.barcode_search, name='barcode_search')]
)

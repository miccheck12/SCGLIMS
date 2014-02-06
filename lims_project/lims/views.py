from __future__ import print_function

import sys

from django.shortcuts import render
from django.http import Http404

from lims.models import Collaborator, Sample, SAGPlate, ExtractedCell


def index(request):
    collaborators = Collaborator.objects.all().order_by('last_name')
    return render(request, 'lims/index.html', {'collaborators': collaborators})


def get_attr_list(obj):
    """Returns a [(key, value), ...] list for given object. The object should
    implement a preffered_ordering function that returns a list of attribute
    names."""
    return [(k, getattr(obj, k)) for k in obj.preferred_ordering()]


def default_object_table(obj):
    def func(request, obj_id):
        o = obj.objects.get(pk=obj_id)
        return render(request, 'lims/object.html',
                      {'objectname': obj.__name__, 'object': o})
    return func


def sample_detail(request, sample_id):
    sample = Sample.objects.get(pk=sample_id)
    extracted_cells = list(ExtractedCell.objects.filter(sample__id=sample_id))
    return render(request, 'lims/sampletree.html',
        {'sample': sample, 'collaborator': sample.collaborator,
        'extractedcells': extracted_cells})


def sagplate_detail(request, sagplate_id):
    sagplate = SAGPlate.objects.get(pk=sagplate_id)
    return render(request, 'lims/table.html',
        {'tablename': 'SAGPlate', 'rows':
        [(k, getattr(sagplate, k)) for k in sagplate.preferred_ordering()]})


def barcode_search(request, barcode):
    if barcode.startswith("SA:"):
        s = list(Sample.objects.filter(uid=barcode[3:]))
        if len(s) == 1:
            return default_object_table(Sample)(request, s[0].id)
        else:
            print("ERR: More than one or zero samples with given barcode", file=sys.stderr)
    raise Http404

from __future__ import print_function

from collections import OrderedDict

import sys

import json

from django.shortcuts import render
from django.http import Http404
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from lims.models import Collaborator, Sample, SAGPlate, SAGPlateDilution, ExtractedCell, SAG


def index(request):
    return render(request, 'lims/index.html')


def browse(request):
    return render(request, 'lims/browse.html')


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


def default_object_list(obj):
    def func(request):
        return render(request, 'lims/object_list.html',
                      {'objectname': obj.__name__, 'objects': list(obj.objects.all())})
    return func


def sample_tree(request, sample_id):
    sample = Sample.objects.get(pk=sample_id)
    sample.extracted_cells = list(ExtractedCell.objects.filter(sample__id=sample_id))
    for ec in sample.extracted_cells:
        ec.sag_plates = list(SAGPlate.objects.filter(extracted_cell__id=ec.id))
        for sp in ec.sag_plates:
            sp.sags = list(SAG.objects.filter(sag_plate__id=sp.id))
            sp.sag_plate_dilutions = list(SAGPlateDilution.objects.filter(sag_plate__id=sp.id))
            for spd in sp.sag_plate_dilutions:
                spd.sags = list(SAG.objects.filter(sag_plate_dilution__id=sp.id))

    return render(request, 'lims/sampletree2.html',
        {'sample': sample})


def generate_related_objects_tree(obj):
    rv = {"url": reverse('lims.views.' + slugify(type(obj).__name__),
                                                 args=[obj.id])}

    for ro in obj._meta.get_all_related_objects():
        for o in getattr(obj, ro.get_accessor_name()).all():
            rv.setdefault(type(o).__name__, {})[str(o)] = generate_related_objects_tree(o)

    return rv


def sample_tree_json(request, sample_id):
    sample = Sample.objects.get(pk=sample_id)

    response_data = {}
    # serializers.serialize("json", [sample])

    #response_data['Sample'] = OrderedDict()
    ##for field in sample.preferred_ordering:
    ##    response_data['Sample'][field] = str(getattr(sample, field))

    #response_data['Sample']["name"] = str(sample)
    #response_data['Sample']["url"] = reverse('lims.views.sample', args=[sample.id])

    response_data['Sample'] = {}
    response_data['Sample'][str(sample)] = generate_related_objects_tree(sample)

    return render(request, 'lims/sampletree3.html',
                  {'json': json.dumps(response_data)})


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


def barcode_index(request):
    return render(request, 'lims/barcode_index.html')


def barcode_search(request, barcode):
    if barcode.startswith("SA:"):
        s = list(Sample.objects.filter(uid=barcode[3:]))
        if len(s) == 1:
            return default_object_table(Sample)(request, s[0].id)
        else:
            print("ERR: More than one or zero samples with given barcode", file=sys.stderr)
    raise Http404

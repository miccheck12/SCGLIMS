from django.shortcuts import render

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
        return render(request, 'lims/objecttable.html',
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
    print dict([(k, getattr(sagplate, k)) for k in sagplate.preferred_ordering()])
    return render(request, 'lims/table.html',
        {'tablename': 'SAGPlate', 'rows':
        [(k, getattr(sagplate, k)) for k in sagplate.preferred_ordering()]})

from django.shortcuts import render

from lims.models import Collaborator, Sample


def index(request):
    collaborators = Collaborator.objects.all().order_by('last_name')
    return render(request, 'lims/index.html', {'collaborators': collaborators})


def sample_detail(request, sample_id):
    sample = Sample.objects.get(pk=sample_id)
    print dict([(k, getattr(sample, k)) for k in sample.preferred_ordering()])
    return render(request, 'lims/table.html', {'tablename': 'Sample', 'rows': [(k, getattr(sample, k)) for k in sample.preferred_ordering()]})

from django.shortcuts import render

from lims.models import Collaborator

# Create your views here.
def index(request):
    collaborators = Collaborator.objects.all().order_by('last_name')
    return render(request, 'lims/index.html', {'collaborators': collaborators})

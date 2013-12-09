from django.contrib import admin
from lims.models import Collaborator, Sample, SampleType, SampleLocation, StorageLocation

for model in [Collaborator, Sample, SampleType, SampleLocation, StorageLocation]:
    admin.site.register(model)

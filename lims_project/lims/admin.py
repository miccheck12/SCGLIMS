from django.contrib import admin
from django.contrib.contenttypes import generic

from lims.models import Collaborator, Sample, SampleType, SampleLocation, \
    StorageLocation, Protocol, ExtractedCell, ExtractedDNA, QPCR, RTMDA, SAGPlate, \
    SAGPlateDilution, DNALibrary, SequencingRun, Metagenome, Primer, \
    Amplicon, SAG, PureCulture, ReadFile

standard_models = [Collaborator, Sample, SampleType, SampleLocation,
              StorageLocation, Protocol, QPCR,
              RTMDA, SAGPlate, SAGPlateDilution, SequencingRun,
              Metagenome, Primer, Amplicon, SAG, PureCulture, ReadFile]

for model in standard_models:
    admin.site.register(model)

class DNALibraryAdmin(admin.ModelAdmin):
    exclude = ('content_type',)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
            if db_field.name == "object_id":
                objects = list(Amplicon.objects.all()) + list(SAG.objects.all()) + \
                    list(PureCulture.objects.all())
                kwargs['choices'] = tuple([(o.id, o.id) for o in objects])
                kwargs['empty_label'] = "---------"
                kwargs['blank'] = False
            return super(DNALibraryAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)

class ExtractedCellAdmin(admin.ModelAdmin):
    readonly_fields = ('replicate_number',)

admin.site.register(DNALibrary, DNALibraryAdmin)
admin.site.register(ExtractedCell, ExtractedCellAdmin)
admin.site.register(ExtractedDNA, ExtractedCellAdmin)

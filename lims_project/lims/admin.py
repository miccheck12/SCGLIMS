from django.contrib import admin

from lims.models import Collaborator, Sample, SampleType, SampleLocation, \
    StorageLocation, Protocol, ExtractedCell, ExtractedDNA, QPCR, RTMDA, SAGPlate, \
    SAGPlateDilution, DNALibrary, SequencingRun, Metagenome, Primer, \
    Amplicon, SAG, PureCulture, ReadFile

standard_models = [SampleType, SampleLocation, StorageLocation, Protocol, QPCR,
                   RTMDA, SequencingRun, Amplicon, SAG,
                   PureCulture, ReadFile]

for model in standard_models:
    admin.site.register(model)


class SampleAdmin(admin.ModelAdmin):
    list_display = [
        'uid',
        'barcode',
        'collaborator',
        'sample_type',
        'sample_location',
        'gps',
        'temperature',
        'ph',
        'salinity',
        'depth',
        'shipping_method',
        'storage_location',
        'storage_medium',
        'biosafety_level',
        'status',
        'notes'
    ]
admin.site.register(Sample, SampleAdmin)

class CollaboratorAdmin(admin.ModelAdmin):
    list_display = [
        'first_name',
        'last_name',
        'institution',
        'phone',
        'email'
    ]
admin.site.register(Collaborator, CollaboratorAdmin)

class ExtractedCellAdmin(admin.ModelAdmin):
    list_display = [
        'uid',
        'barcode',
        'sample',
        'protocol',
        'index_by_sample',
        'protocol',
        'storage_location',
        'notes'
    ]
    readonly_fields = ('index_by_sample', 'uid')
admin.site.register(ExtractedCell, ExtractedCellAdmin)

class ExtractedDNAAdmin(admin.ModelAdmin):
    list_display = [
        'uid',
        'barcode',
        'sample',
        'protocol',
        'index_by_sample',
        'protocol',
        'storage_location',
        'notes'
    ]
    readonly_fields = ('index_by_sample', 'uid')
admin.site.register(ExtractedDNA, ExtractedDNAAdmin)

class SAGPlateAdmin(admin.ModelAdmin):
    list_display = [
        'uid',
        'barcode',
        'extracted_cell',
        'storage_location',
        'protocol',
        'report',
        'qpcr',
        'rt_mda',
        'notes',
    ]
    readonly_fields = ('index_by_sample', 'uid')
admin.site.register(SAGPlate, SAGPlateAdmin)

class SAGPlateDilutionAdmin(admin.ModelAdmin):
    list_display = [
        'uid',
        'barcode',
        'sag_plate',
        'qpcr',
        'dilution',
    ]
    readonly_fields = ('index_by_sample', 'uid')
admin.site.register(SAGPlateDilution, SAGPlateDilutionAdmin)

class DNALibraryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'amplicon',
        'metagenome',
        'sag',
        'pure_culture',
        'buffer',
        'i7',
        'i5',
        'sample_name_on_platform',
        'storage_location',
    ]
admin.site.register(DNALibrary, DNALibraryAdmin)

class PrimerAdmin(admin.ModelAdmin):
    list_display = [
        'concentration',
        'tmelt',
        'storage_location',
        'stock',
    ]
admin.site.register(Primer, PrimerAdmin)

class MetagenomeAdmin(admin.ModelAdmin):
    list_display = [
        'uid',
        'extracted_dna',
        'diversity_report',
    ]
admin.site.register(Metagenome, MetagenomeAdmin)

# DEPRECATED -->
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

def generate_all_fields_admin(classname):
        return type(classname.__name__ + "Admin", (admin.ModelAdmin,),
                    {'list_display': ([name for name in classname._meta.get_all_field_names() if name \
                    not in ['amplicon', 'extractedcell', 'extracteddna',
                            'metagenome', 'id', 'uid','sample']])})
# END DEPRECATED <--

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from import_export.admin import ImportExportModelAdmin

from lims.models import Collaborator, Sample, SampleType, SampleLocation, \
    StorageLocation, Protocol, ExtractedCell, ExtractedDNA, QPCR, RTMDA, SAGPlate, \
    SAGPlateDilution, DNALibrary, SequencingRun, Metagenome, Primer, \
    Amplicon, SAG, PureCulture, ReadFile

from lims.import_export_resources import SampleResource

standard_models = [SampleType, SampleLocation, StorageLocation, QPCR, RTMDA,
                   Amplicon]

for model in standard_models:
    admin.site.register(model)

def create_modeladmin(modeladmin, model, name = None):
    class  Meta:
        proxy = True
        app_label = model._meta.app_label

    attrs = {'__module__': '', 'Meta': Meta}

    newmodel = type(name, (model,), attrs)

    admin.site.register(newmodel, modeladmin)
    return modeladmin


class SampleAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = SampleResource
    editables = [
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
    ]
    list_display = [
        'id',
        'uid',
        'barcode',
    ] + editables

    class Media:
        js = ('lims/admin_edit_button.js',)

    def response_change(self, request, obj, post_url_continue=None):
        """This makes the response after changing go back to parameterless
        overview (maybe not necessary)."""
        return HttpResponseRedirect(reverse("admin:lims_sample_changelist"))

    def changelist_view(self, request, extra_context=None):
        # Make editable if e is given as GET value
        if request.method == "GET" and 'e' in request.GET:
            self.list_editable = self.editables
        else:
            self.list_editable = []

        # redirect to parameterless if object is saved
        if "_save" in request.POST:
            return HttpResponseRedirect(reverse("admin:lims_sample_changelist"))

        return super(SampleAdmin, self).changelist_view(request,
                                                        extra_context=extra_context)

admin.site.register(Sample, SampleAdmin)

class CollaboratorAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'first_name',
        'last_name',
        'institution',
        'phone',
        'email'
    ]
admin.site.register(Collaborator, CollaboratorAdmin)

class ExtractedCellAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'uid',
        'barcode',
        'sample',
        'protocol',
        'index_by_group',
        'protocol',
        'storage_location',
        'notes'
    ]
    readonly_fields = ('index_by_group', 'uid')
admin.site.register(ExtractedCell, ExtractedCellAdmin)

class ExtractedDNAAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'uid',
        'barcode',
        'sample',
        'protocol',
        'index_by_group',
        'protocol',
        'storage_location',
        'notes'
    ]
    readonly_fields = ('index_by_group', 'uid')
admin.site.register(ExtractedDNA, ExtractedDNAAdmin)

class SAGPlateAdmin(admin.ModelAdmin):
    list_display = [
        'id',
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
    readonly_fields = ('index_by_group', 'uid')
admin.site.register(SAGPlate, SAGPlateAdmin)

class SAGPlateDilutionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'uid',
        'barcode',
        'sag_plate',
        'qpcr',
        'dilution',
    ]
    readonly_fields = ('index_by_group', 'uid')
admin.site.register(SAGPlateDilution, SAGPlateDilutionAdmin)

class DNALibraryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'uid',
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
    readonly_fields = ('index_by_group', 'uid')
admin.site.register(DNALibrary, DNALibraryAdmin)

class PrimerAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'concentration',
        'tmelt',
        'storage_location',
        'stock',
    ]
admin.site.register(Primer, PrimerAdmin)

class MetagenomeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'uid',
        'extracted_dna',
        'diversity_report',
    ]
admin.site.register(Metagenome, MetagenomeAdmin)

class SAGAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'uid',
        'sag_plate',
        'sag_plate_dilution',
        'well',
        'concentration'
    ]
admin.site.register(SAG, SAGAdmin)

class PureCultureAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'uid',
        'extracted_dna',
        'concentration'
    ]
admin.site.register(PureCulture, PureCultureAdmin)

class SequencingRunAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'uid',
        'date',
        'sequencing_center',
        'machine',
        'report',
        'folder',
        'notes',
        'protocol',
    ]
admin.site.register(SequencingRun, SequencingRunAdmin)

class ReadFileAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'filename',
        'pair',
        'lane',
        'read_count',
        'dna_library',
        'sequencing_run',
    ]
admin.site.register(ReadFile, ReadFileAdmin)

class ProtocolAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'revision',
        'link',
        'notes',
    ]
admin.site.register(Protocol, ProtocolAdmin)

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

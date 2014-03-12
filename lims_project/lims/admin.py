from django.contrib import admin
from django.contrib.admin.models import LogEntry, DELETION
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from import_export.admin import ImportExportModelAdmin

from lims.models import Apparatus, ApparatusSubdivision, Collaborator, Sample, SampleType, SampleLocation, \
    Protocol, ExtractedCell, ExtractedDNA, QPCR, RTMDA, SAGPlate, \
    SAGPlateDilution, DNALibrary, SequencingRun, Metagenome, Primer, \
    Amplicon, SAG, DNAFromPureCulture, ReadFile, Container

from lims.import_export_resources import SampleResource

standard_models = [QPCR, RTMDA, Apparatus]

for model in standard_models:
    admin.site.register(model)


def create_modeladmin(modeladmin, model, name=None):
    class Meta:
        proxy = True
        app_label = model._meta.app_label

    attrs = {'__module__': '', 'Meta': Meta}

    newmodel = type(name, (model,), attrs)

    admin.site.register(newmodel, modeladmin)
    return modeladmin


class AmpliconAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'uid',
        'sample',
        'extracted_dna',
        'index_by_group',
        'diversity_report',
        'container',
        'buffer',
        'notes',
    ]
    readonly_fields = ('index_by_group', 'uid')
admin.site.register(Amplicon, AmpliconAdmin)


class ContainerApparatusFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Apparatus')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'apparatus'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [(ap.id, _(str(ap))) for ap in Apparatus.objects.all()]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        all_aps = [aps.id for aps in ApparatusSubdivision.objects.all()]
        if self.value():
            aps = [aps.id for aps in ApparatusSubdivision.objects.filter(apparatus=self.value())]
            cons = Container.objects.filter(apparatus_subdivision__in=aps)
            return queryset & cons


class ContainerAdmin(admin.ModelAdmin):
    list_filter = [
        'type',
        ContainerApparatusFilter,
    ]
    list_display = [
        'id',
        'barcode',
        'root_apparatus',
        'root_apparatus_subdivision',
        'type',
        'row',
        'column',
        'parent',
        'get_nr_children',
    ]

    def get_nr_children(self, obj):
        return "%s" % str(obj.child.count())
    get_nr_children.short_description = "No of Children"
admin.site.register(Container, ContainerAdmin)


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
        'container',
        'biosafety_level',
        'status',
    ]
    list_display = [
        'id',
        'uid',
        'barcode',
    ] + editables
    # import_export change template to include csv
    import_template_name = 'import_export/lims_import.html'

    #class Media:
    #    js = ('lims/admin_edit_button.js',)

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
    raw_id_fields = ("container",)

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
        'container',
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
        'container',
        'concentration',
        'buffer',
        'notes',
    ]
    readonly_fields = ('index_by_group', 'uid')
admin.site.register(ExtractedDNA, ExtractedDNAAdmin)


class SAGPlateAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'uid',
        'barcode',
        'extracted_cell',
        'apparatus_subdivision',
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
        'container',
    ]
    readonly_fields = ('index_by_group', 'uid')
admin.site.register(DNALibrary, DNALibraryAdmin)


class PrimerAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'concentration',
        'tmelt',
        'container',
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


class DNAFromPureCultureAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'uid',
        'extracted_dna',
        'concentration'
    ]
admin.site.register(DNAFromPureCulture, DNAFromPureCultureAdmin)


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
    filter_horizontal = ['dna_library']
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


class LogEntryAdmin(admin.ModelAdmin):
    """From: https://djangosnippets.org/snippets/2484/"""
    date_hierarchy = 'action_time'
    readonly_fields = LogEntry._meta.get_all_field_names()
    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]
    search_fields = [
        'object_repr',
        'change_message'
    ]
    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
        'change_message',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = u'<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return link
    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'

    def queryset(self, request):
        return super(LogEntryAdmin, self).queryset(request) \
            .prefetch_related('content_type')

admin.site.register(LogEntry, LogEntryAdmin)


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
                    {'list_display': ([name for name in classname._meta.get_all_field_names() if name
                    not in ['amplicon', 'extractedcell', 'extracteddna',
                            'metagenome', 'id', 'uid', 'sample']])})
# END DEPRECATED <--

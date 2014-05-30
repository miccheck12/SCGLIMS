from __future__ import print_function
import sys

from django.contrib import admin
from django.contrib.admin.models import LogEntry, DELETION
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from import_export.admin import ImportExportModelAdmin

from lims.models import Apparatus, ApparatusSubdivision, Collaborator, Sample, SampleType, SampleLocation, \
    Protocol, ExtractedCell, ExtractedDNA, QPCR, RTMDA, SAGPlate, \
    SAGPlateDilution, DNALibrary, SequencingRun, Metagenome, Primer, \
    Amplicon, SAG, DNAFromPureCulture, ReadFile, Container, ContainerType, BarcodePrinter, BarcodeToModel

from lims.import_export_resources import SampleResource, ContainerResource

from sh import lpr


def generate_all_fields_admin(classname):
    """Generate an Admin class which adds all fields to list_display except for
    notes."""
    #TODO: extend this for IndexByGroup models with read_only_fields/uid
    #TODO: show ForeignKeyFields that are not reversely related
    return type(classname.__name__ + "Admin", (admin.ModelAdmin,),
                {'list_display': ([f.name for (f, model) in
                                   classname._meta.get_fields_with_model() if
                                   model is None and f.name not in
                                   ["notes"]])})

# Generate standard admin classes for the standard_models
standard_models = [QPCR, RTMDA, Apparatus, ApparatusSubdivision, SampleLocation, SampleType, ContainerType, BarcodePrinter, BarcodeToModel]
for model in standard_models:
    admin.site.register(model, generate_all_fields_admin(model))


def print_barcode(modeladmin, request, queryset):
    for q in queryset:
        ct = ContentType.objects.get_for_model(queryset.model)
        btm = BarcodeToModel.objects.get(content_type=ct)
        fields = [getattr(q, f) for f in btm.barcode_fields.split()]
        print("len: %d" % len(fields), file=sys.stderr)
        # add extra fields if not enough fields are given
        if len(fields) < 4:
            fields += (4 - len(fields)) * [""]
        out = btm.barcode.template.format(*fields)
        print(out, file=sys.stderr)
        lpr("-P", btm.barcode.name, _in=out)
print_barcode.short_description = "Print barcode"


class ContainerInline(generic.GenericTabularInline):
    model = Container
    raw_id_fields = ("parent",)
    extra = 0


class AmpliconAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'uid',
        'sample',
        'extracted_dna',
        'index_by_group',
        'diversity_report',
        'buffer',
        'notes',
    ]
    readonly_fields = ('index_by_group', 'uid')
    inlines = [
        ContainerInline,
    ]
    raw_id_fields = ("extracted_dna",)
admin.site.register(Amplicon, AmpliconAdmin)


class ContainerApparatusFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Apparatus')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'apparatus'

    def lookups(self, request, model_admin):
        """The options are the different Apparatus objects"""
        return [(ap.id, _(str(ap))) for ap in Apparatus.objects.all()]

    def queryset(self, request, queryset):
        """Only return containers where the apparatus root is set to given value"""
        if self.value():
            con_ids = [c.id for c in queryset if c.root_apparatus.id == int(self.value())]
            return queryset.filter(id__in=con_ids)


class ContainerIsEmptyFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Is Empty')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'is_empty'

    def lookups(self, request, model_admin):
        """only True and False for is_empty"""
        return [(True, _(str(True))), (False, _(str(False)))]

    def queryset(self, request, queryset):
        """If a value is specified only return is_empty with the same value"""
        if self.value():
            empty_ids = [c.id for c in queryset if c.is_empty == (self.value() == "True")]
            return queryset.filter(id__in=empty_ids)


class ContainerAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ContainerResource
    list_filter = [
        'date',
        'type',
        ContainerApparatusFilter,
        ContainerIsEmptyFilter,
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
        'nr_objects_in_container',
        'is_empty',
        'date',
    ]
    #search_fields = ("parent",)
    raw_id_fields = ("parent",)
    list_per_page = 10
    # import_export change template to include csv
    import_template_name = 'import_export/lims_import.html'

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
        'temperature',
        'ph',
        'salinity',
        'depth',
        'shipping_method',
        'status',
    ]
    list_display = [
        'id',
        'uid',
        'barcode',
    ] + editables
    # import_export change template to include csv
    import_template_name = 'import_export/lims_import.html'
    inlines = [
        ContainerInline,
    ]
    actions = [print_barcode]

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
        'notes'
    ]
    inlines = [
        ContainerInline,
    ]
    readonly_fields = ('index_by_group', 'uid')
    raw_id_fields = ("sample",)
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
        'concentration',
        'buffer',
        'notes',
    ]
    inlines = [
        ContainerInline,
    ]
    readonly_fields = ('index_by_group', 'uid')
    raw_id_fields = ("sample",)
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
    raw_id_fields = ("extracted_cell",)
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
    raw_id_fields = ("sag_plate",)
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
    ]
    inlines = [
        ContainerInline,
    ]
    readonly_fields = ('index_by_group', 'uid')
    raw_id_fields = ("amplicon", "metagenome", "sag", "pure_culture")
admin.site.register(DNALibrary, DNALibraryAdmin)


class PrimerAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'concentration',
        'tmelt',
        'stock',
    ]
    inlines = [
        ContainerInline,
    ]
admin.site.register(Primer, PrimerAdmin)


class MetagenomeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'uid',
        'extracted_dna',
        'diversity_report',
    ]
    readonly_fields = ('index_by_group', 'uid')
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
    readonly_fields = ('index_by_group', 'uid')
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

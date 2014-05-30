from __future__ import print_function
import sys
import re

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.admin.models import LogEntry
from django.template.defaultfilters import slugify


def property_verbose(description):
    """Make the function a property and give it a description. Normal property
    decoration does not work with short_description"""
    def property_verbose_inner(function):
        function.short_description = description
        return property(function)
    return property_verbose_inner


class UIDManager(models.Manager):
    def get_by_natural_key(self, uid):
        return self.get(uid=uid)


class Apparatus(models.Model):
    """Device that stores physical objects, could be a closet/freezer, etc."""
    name = models.CharField(max_length=100)
    temperature = models.DecimalField(u"Temperature \u00B0C", max_digits=10,
        decimal_places=2, blank=True, null=True)
    location = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        verbose_name_plural = "Apparatus"

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [
            'id',
            'name',
            'temperature',
            'location',
            'date',
        ]


class ApparatusSubdivision(models.Model):
    """An apparatus can have multiple shelves or racks. If the machine has only
    one location to store things it should still have a record here, see
    Container documentation."""
    name = models.CharField(max_length=100)
    apparatus = models.ForeignKey(Apparatus)
    date = models.DateTimeField(default=timezone.now, blank=True)

    def __unicode__(self):
        return unicode("{0} {1}".format(self.apparatus, self.name))

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [
            'id',
            'name',
            'apparatus',
            'date',
        ]


class BarcodePrinter(models.Model):
    name = models.CharField(max_length=100)
    template = models.TextField(blank=True)

    def __unicode__(self):
        return unicode(self.name)


class BarcodeToModel(models.Model):
    qlimit = \
        models.Q(app_label="lims", model="sample") | \
        models.Q(app_label="lims", model="primer") | \
        models.Q(app_label="lims", model="extractedcell") | \
        models.Q(app_label="lims", model="extracteddna") | \
        models.Q(app_label="lims", model="amplicon") | \
        models.Q(app_label="lims", model="sagplate") | \
        models.Q(app_label="lims", model="sagplatedilution") | \
        models.Q(app_label="lims", model="dnalibrary")
    content_type = models.ForeignKey(ContentType, limit_choices_to=qlimit, null=True, blank=True)
    barcode = models.ForeignKey(BarcodePrinter)
    barcode_fields = models.TextField(blank=True, help_text="Specify space-separated list of fields")

    def __unicode__(self):
        return unicode("{0} - {1}".format(self.barcode, self.content_type))


class CanPrintBarcode(object):
    def print_barcode(self):
        return "ola"


class ContainerType(models.Model):
    """The type of container e.g. petri dish, 384 well plate, bag, well,
    etc."""
    name = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now, blank=True)
    divisible = models.BooleanField(default=False)
    barcode = models.ForeignKey(BarcodePrinter, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [
            'id',
            'name',
            'notes',
            'date',
        ]


class Container(models.Model):
    """A container can hold samples or other physical objects. They have a
    type, explained in ContainerType. They have a parent and child field used
    to subdivide a Container in multiple Containers, e.g. a 384 well plate
    Container into 384 well Containers. The root parent Container is always
    linked to a single ApparatusSubDivision so never to an Apparatus itself.
    The children Containers should leave the apparatus_subdivision field empty
    to avoid redundancy and inconsistencies between the root parent Container
    and its children."""
    type = models.ForeignKey(ContainerType)
    row = models.IntegerField(blank=True, null=True)
    column = models.IntegerField(blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True,
                               help_text="Parent container",
                               related_name="child")
    apparatus_subdivision = models.ForeignKey(ApparatusSubdivision, blank=True,
                                              null=True)
    notes = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now, blank=True)

    # Generic relation
    qlimit = models.Q(app_label="lims", model="sample") | \
             models.Q(app_label="lims", model="primer") | \
             models.Q(app_label="lims", model="extractedcell") | \
             models.Q(app_label="lims", model="extracteddna") | \
             models.Q(app_label="lims", model="amplicon") | \
             models.Q(app_label="lims", model="dnalibrary")
    content_type = models.ForeignKey(ContentType, limit_choices_to=qlimit, null=True, blank=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    @property
    def barcode(self):
        return "CO:%06d" % (self.pk if self.pk else 0)

    @property_verbose("Root")
    def root(self):
        # Follow Container to root
        root = self
        while root.parent is not None:
            root = root.parent
        return root

    @property_verbose("Apparatus")
    def root_apparatus(self):
        return self.root_apparatus_subdivision.apparatus

    @property_verbose("Apparatus subdivision")
    def root_apparatus_subdivision(self):
        try:
            return self.root.apparatus_subdivision
        except:
            raise(Exception("Database inconsistency! If parent is null, "
                "apparatus_subdivision should be set"))

    def save(self):
        """Saves and checks whether either parent or apparatus_subdivision is
        provided. Only the root Container with parent null should be linked to
        an apparatus_subdivision."""
        if bool(self.parent) != bool(self.apparatus_subdivision):
            super(Container, self).save()
        else:
            raise(Exception("The root container should be linked to an "
            "apparatus_subdivision. Child containers not."))

    def __unicode__(self):
        return unicode("%s-%s") % (self.type, self.barcode)

    def clean(self):
        if bool(self.parent) and bool(self.apparatus_subdivision):
            error_msg = """A container with a parent can't be located at a
            different location than it's parent i.e. specify either parent or
            apparatus_subdivision."""
            raise ValidationError({"parent": [error_msg, ],
                                   "apparatus_subdivision": [error_msg, ]})
        elif not bool(self.parent) and not bool(self.apparatus_subdivision):
            error_msg = """A container without a parent should be stored at an
            apparatus_subdivision."""
            raise ValidationError({"parent": [error_msg, ],
                                   "apparatus_subdivision": [error_msg, ]})
        super(Container, self).clean()

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [
            'id',
            'type',
            'row',
            'column',
            'parent',
            'apparatus_subdivision',
            'notes',
            'date',
        ]

    @property
    def is_root(self):
        """Check if container is a root container"""
        return self.parent is None

    @property
    def is_leaf(self):
        """Check if container is a leaf container"""
        return len(self.child.all()) == 0

    def get_objects_in_container(self):
        """Get all objects in the container. If this is not a leaf container,
        also get child objects."""
        if self.is_leaf:
            return [] if self.is_empty else [self.content_object]
        else:
            objects = []
            for c in self.child.all():
                objects.extend(c.get_objects_in_container())
            return objects

    @property
    def nr_objects_in_container(self):
        """Count number of objects in the container"""
        if self.is_leaf:
            return 0 if self.is_empty else 1
        else:
            count = 0
            for c in self.child.all():
                if c.is_leaf:
                    count += 1
            return count

    @property
    def is_empty(self):
        """Checks if the container is empty. If the container is not a leaf
        container, also check child containers."""
        return self.object_id is None

    class Meta:
        unique_together = (("row", "column", "parent"),)


class StorablePhysicalObject(models.Model):
    def clean(self):
        for c in self.containers.all():
            if c.type.divisible:
                error_msg = "Container {0} is divisible. You should store it in"
                "a container that can't be subdivided any further.".format(c)
                raise(ValidationError({"containers": [error_msg, ]}))
            super(StorablePhysicalObject, self).clean()

    class Meta:
        abstract = True

    containers = generic.GenericRelation(Container,
                                         content_type_field="content_type",
                                         object_id_field="object_id")


#class StorablePhysicalObject(models.Model):
#    container = models.OneToOneField(Container, blank=True, null=True)
#
#    def clean(self):
#        if self.container:
#            if not self.container.is_leaf():
#                error_msg = "Container {0} is not a leaf container!".format(self.container)
#                raise(ValidationError({"container": [error_msg, ]}))
#            if self.container.nr_objects_in_container > 1:
#                error_msg = """Container {0} is not empty. It contains
#                    {1} objects i.e. {2}.""".format(self.container,
#                                                    self.container.nr_objects_in_container,
#                                                    self.container.get_objects_in_container())
#                raise(ValidationError({"container": [error_msg, ]}))
#        super(StorablePhysicalObject, self).clean()
#
#    class Meta:
#        abstract = True
#


class IndexByGroup(models.Model):
    """IndexByGroup allows one to group a model by another model and get the
    index based on that. An attribute character_list can be given to support a
    naming scheme that converts the indexes to characters."""
    def get_count_by_group(self):
        """Count the number of objects related to the object's group"""
        return self.__class__.objects.filter(**{self.group_id_keyword: self.group.id}).count()

    def get_max_by_group(self):
        """Gives the maximum index_by_group."""
        return self.__class__.objects.filter(
            **{self.group_id_keyword: self.group.id}).aggregate(
            models.Max('index_by_group'))['index_by_group__max']

    def calc_index_by_group(self):
        """Returns index_by_group and calculates it if non-existent"""
        # calculate if this is a new instance
        if self.pk is None:
            index_by_group = self.get_count_by_group()
            if hasattr(self, 'character_list') \
              and index_by_group >= len(self.character_list):
                raise(Exception("Too many objects, only %i %s supported by "
                                "naming scheme" % (len(self.character_list),
                                                self.__class__)))
            return index_by_group
        else:
            try:
                return self.index_by_group
            except AttributeError:
                raise(Exception("Object has pk but no index_by_group"))

    def save(self):
        """Determine index_by_group on save"""
        if self.pk is None:
            self.index_by_group = self.calc_index_by_group()
        super(IndexByGroup, self).save()

    def index_to_naming_scheme(self):
        try:
            print(self.index_by_group, file=sys.stderr)
            return self.character_list[self.index_by_group]
        except IndexError:
            raise(Exception("Too many objects, only %i %s supported by naming"
                            "scheme" % (len(self.character_list),
                                        self.__class__)))

    @classmethod
    def naming_scheme_to_index(cls, name):
        try:
            return cls.character_list.index(name)
        except AttributeError:
            return int(name)
        except ValueError as e:
            raise e

    class Meta:
        abstract = True

    index_by_group = models.IntegerField(default="Automatically generated")


class Collaborator(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    notes = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now, blank=True)

    def __unicode__(self):
        return unicode("%s %s" % (self.first_name, self.last_name))

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [f.attname for f in self._meta.fields]


class SampleType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now, blank=True)

    def __unicode__(self):
        return unicode("%s" % (self.name))

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [f.attname for f in self._meta.fields]


class SampleLocation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now, blank=True)

    def __unicode__(self):
        return unicode("%s" % (self.name))

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [f.attname for f in self._meta.fields]


class Sample(StorablePhysicalObject, models.Model):
    uid = models.CharField("UID", max_length=30, unique=True,
        help_text="UID should consist of five alphanumeric characters. Only capitals allowed.")

    collaborator = models.ForeignKey(Collaborator)
    sample_type = models.ForeignKey(SampleType)
    sample_location = models.ForeignKey(SampleLocation)

    temperature = models.DecimalField(u"Temperature \u00B0C", max_digits=10,
        decimal_places=2, blank=True, null=True)
    ph = models.DecimalField(" pH", max_digits=10, decimal_places=2, blank=True, null=True)
    salinity = models.DecimalField("Salinity unit(?))", max_digits=10, decimal_places=2, blank=True, null=True)
    depth = models.DecimalField("Depth (m)", max_digits=10, decimal_places=2, blank=True, null=True)
    # Latitude/Longitude decimals like decimal degress with plus and minus.
    # Minus is south of the equator, positive implies north.
    latitude = models.DecimalField(max_digits=13, decimal_places=8, blank=True,
                                   null=True,
                                   validators=[MinValueValidator(-90),
                                               MaxValueValidator(90)])
    # Minus is west of the prime meridian, positive implies east
    longitude = models.DecimalField(max_digits=13, decimal_places=8, blank=True,
                                   null=True,
                                   validators=[MinValueValidator(-180),
                                               MaxValueValidator(180)])
    shipping_method = models.CharField(max_length=30, blank=True)
    date_received = models.DateTimeField(default=timezone.now, blank=True)
    date = models.DateTimeField(default=timezone.now, blank=True)
    biosafety_level = models.IntegerField(
        choices=((1, 1), (2, 2), (3, 3), (4, 4)), blank=True, null=True)
    status = models.CharField(max_length=8,
        choices=(('new', 'new'), ('used', 'used'), ('finished', 'finished')), blank=True, null=True)
    notes = models.TextField(blank=True)
    extra_columns_json = models.TextField(blank=True)

    objects = UIDManager()

    def natural_key(self):
        return self.uid

    @property
    def barcode(self):
        return "SA:" + str(self.uid)

    def __unicode__(self):
        return unicode("%s" % (self.uid))

    def clean(self):
        if re.match("^[A-Z0-9]{5}$", str(self.uid)) is None:
            error_msg = """UID should consist of five alphanumeric characters. Only capitals allowed."""
            raise(ValidationError({"uid": [error_msg, ]}))
        super(Sample, self).clean()

    @classmethod
    def get_by_uid(cls, uid):
        s = list(cls.objects.filter(uid=barcode[3:]))
        if len(s) == 1:
            return s[0]
        else:
            raise(Exception("ERR: More than one or zero objects with given barcode"))

    @classmethod
    def get_by_barcode(cls, barcode):
        return cls.get_by_uid(barcode[3:])

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [
            'id',
            'uid',
            'barcode',
            'collaborator',
            'sample_type',
            'sample_location',
            'latitude',
            'longitude',
            'temperature',
            'ph',
            'salinity',
            'depth',
            'shipping_method',
            'biosafety_level',
            'status',
            'notes',
            'container',
            'date',
        ]

    @property
    def username(self):
        ct = ContentType.objects.get_for_model(self.__class__)
        return LogEntry.objects.filter(content_type=ct).first().user.username


class Protocol(models.Model):
    name = models.CharField(max_length=30)
    revision = models.CharField(max_length=30)
    link = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now, blank=True)

    def __unicode__(self):
        return unicode("%s" % (self.name))


class ExtractedCell(StorablePhysicalObject, IndexByGroup):
    sample = models.ForeignKey(Sample)
    protocol = models.ForeignKey(Protocol)
    notes = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now, blank=True)
    uid = models.CharField("UID", max_length=30, unique=True, default="Automatically generated",
        help_text="UID consists of the sample UID followed by a count i.e. 10Y31_1")

    group_id_keyword = "sample__id"

    objects = UIDManager()

    def natural_key(self):
        return self.uid

    @property
    def group(self):
        return self.sample

    @property
    def barcode(self):
        return "EC:%s" % str(self.uid)

    def save(self):
        """Stores UID on save"""
        if self.pk is None:
            self.index_by_group = self.calc_index_by_group()
            self.uid = "%s_%s" % (self.group.uid, self.index_by_group + 1)
        super(ExtractedCell, self).save()

    def __unicode__(self):
        return unicode(self.uid)

    @property
    def preferred_ordering(self):
        return [
            'id',
            'sample',
            'protocol',
            'container',
            'notes',
        ]


class ExtractedDNA(StorablePhysicalObject, IndexByGroup):
    sample = models.ForeignKey(Sample, null=True, blank=True)
    protocol = models.ForeignKey(Protocol)
    notes = models.TextField(blank=True)
    extracted_cell = models.ForeignKey(ExtractedCell, null=True, blank=True)
    concentration = models.DecimalField(u"Concentration (mol L\u207B\u00B9)",
                                        max_length=100, max_digits=10,
                                        decimal_places=5)
    buffer = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now, blank=True)
    uid = models.CharField("UID", max_length=30, unique=True, default="Automatically generated",
        help_text="UID consists of the sample UID followed by a count i.e. 10Y31_1")

    objects = UIDManager()

    def natural_key(self):
        return self.uid

    @property
    def group_id_keyword(self):
        return "sample__id" if self.sample else "extracted_cell__sample__id"

    @property
    def group(self):
        return self.sample if self.sample else self.extracted_cell.sample

    @property
    def barcode(self):
        return "ED:" + str(self.uid)

    def save(self):
        """Saves and checks whether either Sample or ExtractedCell is provided.
        Not both, because this makes it easier to change the Sample on an
        ExtractedCell for example. Otherwise you would have to change both this
        object and the Extracted Cell."""
        if bool(self.sample) != bool(self.extracted_cell):
            if self.pk is None:
                self.index_by_group = self.calc_index_by_group()
                self.uid = "%s_%s" % (self.group.uid, self.index_by_group + 1)
            super(ExtractedDNA, self).save()
        else:
            raise(Exception("You have to specify an Extracted cell or"
                            " a Sample, but not both."))

    def clean(self):
        if bool(self.sample) == bool(self.extracted_cell):
            error_msg = """You have to specify either an Extracted cell or a
            Sample, but not both."""
            raise(ValidationError({"sample": [error_msg, ], "extracted_cell":
                                   [error_msg, ]}))
        super(ExtractedDNA, self).clean()

    class Meta:
        verbose_name = "Extracted DNA"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return unicode(self.uid)

    @property
    def preferred_ordering(self):
        return [
            'id',
            'uid',
            'sample',
            'protocol',
            'container',
            'notes',
            'extracted_cell',
            'concentration',
            'buffer',
            'container',
        ]


class QPCR(models.Model):
    report = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now, blank=True)

    class Meta:
        verbose_name = "QPCR"
        verbose_name_plural = "QPCRs"

    def __unicode__(self):
        return unicode(self.report)

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [f.attname for f in self._meta.fields]


class RTMDA(models.Model):
    report = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now, blank=True)

    class Meta:
        verbose_name = "RT-MDA kinetics"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return unicode(self.report)

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [f.attname for f in self._meta.fields]


class SAGPlate(IndexByGroup):
    """SAGPlate is not a Container because we want to enforce all the same
    samples on the child wells and in addition store information about the
    Plate itself. The storage location is a key to ApparatusSubDivision,
    similar to Container."""
    report = models.CharField(max_length=100)
    protocol = models.ForeignKey(Protocol)
    apparatus_subdivision = models.ForeignKey(ApparatusSubdivision)
    notes = models.TextField(blank=True)
    extracted_cell = models.ForeignKey(ExtractedCell)
    rt_mda = models.ForeignKey(RTMDA)
    qpcr = models.ForeignKey(QPCR)
    date = models.DateTimeField(default=timezone.now, blank=True)
    uid = models.CharField("UID", max_length=30, unique=True, default="Automatically generated",
        help_text="UID consists of the sample UID followed by a a character [A-Z] i.e. 10Y31A")

    group_id_keyword = "extracted_cell__sample__id"
    character_list = [chr(ord('A') + i) for i in range(26)]  # [A-Z]

    objects = UIDManager()

    def natural_key(self):
        return self.uid

    @property
    def sample(self):
        return self.group

    @property
    def group(self):
        return self.extracted_cell.sample

    @property
    def barcode(self):
        return "SP:" + str(self.uid)

    def save(self):
        """Stores UID on save"""
        if self.pk is None:
            self.index_by_group = self.calc_index_by_group()
            self.uid = self.group.uid + self.index_to_naming_scheme()
        super(SAGPlate, self).save()

    class Meta:
        verbose_name = "SAG plate"
        verbose_name_plural = verbose_name + "s"

    def __unicode__(self):
        return unicode(self.uid)

    @property
    def preferred_ordering(self):
        return ['id',
                'uid',
                'barcode',
                'extracted_cell',
                'apparatus_subdivision',
                'protocol',
                'report',
                'qpcr',
                'rt_mda',
                'notes']


class SAGPlateDilution(IndexByGroup):
    sag_plate = models.ForeignKey(SAGPlate)
    apparatus_subdivision = models.ForeignKey(ApparatusSubdivision)
    dilution = models.CharField(max_length=100)
    qpcr = models.ForeignKey(QPCR)
    notes = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now, blank=True)
    uid = models.CharField("UID", max_length=30, unique=True, default="Automatically generated",
        help_text="UID consists of the sample UID followed by a character or count [a-z0-9] i.e. 10Y31a")

    group_id_keyword = "extracted_cell__sample__id"
    character_list = [chr(ord('a') + i) for i in range(26)] + range(10)  # [a-z0-9]

    objects = UIDManager()

    def natural_key(self):
        return self.uid

    @property
    def sample(self):
        return self.group

    @property
    def group(self):
        return self.sag_plate.extracted_cell.sample

    @property
    def barcode(self):
        return "SD:" + str(self.uid)

    def save(self):
        """Stores UID on save"""
        if self.pk is None:
            self.index_by_group = self.calc_index_by_group()
            self.uid = self.group.uid + self.index_to_naming_scheme()
        super(SAGPlateDilution, self).save()

    class Meta:
        verbose_name = "SAG plate dilution"
        verbose_name_plural = verbose_name + "s"

    def __unicode__(self):
        return unicode(self.uid)

    @property
    def preferred_ordering(self):
        return ['id',
                'uid',
                'barcode',
                'sag_plate',
                'dilution',
                'qpcr',
                'notes']


class Metagenome(IndexByGroup):
    extracted_dna = models.ForeignKey(ExtractedDNA)
    diversity_report = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now, blank=True)
    uid = models.CharField("UID", max_length=30, unique=True, default="Automatically generated",
        help_text="UID consists of the sample UID followed by A_X and count [01-99] i.e. 10Y31A_X01")

    group_id_keyword = "extracted_dna__sample__id"
    character_list = ["%02d" % i for i in range(1, 100)]  # [01-99]

    objects = UIDManager()

    def natural_key(self):
        return self.uid

    @property
    def sample(self):
        return self.group

    @property
    def group(self):
        return self.extracted_dna.sample

    def __unicode__(self):
        return unicode(self.uid)

    def save(self):
        """Stores UID on save"""
        if self.pk is None:
            self.index_by_group = self.calc_index_by_group()
            self.uid = self.group.uid + "A_X" + self.index_to_naming_scheme()
        super(Metagenome, self).save()

    @property
    def preferred_ordering(self):
        return ['id',
                'uid',
                'diversity_report',
                'date']


class Primer(StorablePhysicalObject):
    sequence = models.TextField()
    tmelt = models.DecimalField(u"tmelt (\u00B0C)", max_digits=10,
                                decimal_places=2)
    concentration = models.DecimalField(u"Concentration (mol L\u207B\u00B9)",
                                        max_length=100, max_digits=10,
                                        decimal_places=5)
    stock = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now, blank=True)

    def __unicode__(self):
        return unicode("Primer %d" % self.pk)

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [f.attname for f in self._meta.fields]


class Amplicon(StorablePhysicalObject, IndexByGroup):
    extracted_dna = models.ForeignKey(ExtractedDNA)
    diversity_report = models.CharField(max_length=100)
    buffer = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    primer = models.ManyToManyField(Primer)
    date = models.DateTimeField(default=timezone.now, blank=True)
    uid = models.CharField("UID", max_length=30, unique=True, default="Automatically generated",
        help_text="UID consists of the sample UID followed by A_Y and count [01-99] i.e. 10Y31A_Y01")

    group_id_keyword = "extracted_dna__sample__id"
    character_list = ["%02d" % i for i in range(1, 100)]  # [01-99]

    objects = UIDManager()

    def natural_key(self):
        return self.uid

    @property
    def sample(self):
        return self.group

    @property
    def group(self):
        return self.extracted_dna.sample

    @property
    def barcode(self):
        return "AM:" + str(self.uid)

    def save(self):
        """Stores UID on save"""
        if self.pk is None:
            self.index_by_group = self.calc_index_by_group()
            self.uid = self.group.uid + "A_Y" + self.index_to_naming_scheme()
        super(Amplicon, self).save()

    def __unicode__(self):
        return unicode(self.uid)

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [f.attname for f in self._meta.fields]


class SAG(models.Model):
    sag_plate = models.ForeignKey(SAGPlate, blank=True, null=True)
    sag_plate_dilution = models.ForeignKey(SAGPlateDilution, blank=True, null=True)
    well = models.CharField(max_length=3)
    concentration = models.DecimalField(u"Concentration (mol L\u207B\u00B9)",
                                        max_length=100, max_digits=10,
                                        decimal_places=5)
    date = models.DateTimeField(default=timezone.now, blank=True)
    uid = models.CharField("UID", max_length=30, unique=True, default="Automatically generated",
        help_text="UID consists of the SAGPlate or SAGPlateDilution UID followed by the well i.e. 10Y31A_O10")

    objects = UIDManager()

    def natural_key(self):
        return self.uid

    def save(self):
        if sum((bool(self.sag_plate_dilution),
                bool(self.sag_plate))) == 1:
            if self.pk is None:
                sag_plate_uid = self.sag_plate.uid if self.sag_plate else \
                    self.sag_plate_dilution.uid
                self.uid = "%s_%s" % (sag_uid, self.well)
            super(SAG, self).save()
        else:
            raise(Exception("You have to specify either a SAGPlate or a "
                            "SAGPlateDilution and not both"))

    def clean(self):
        if bool(self.sag_plate_dilution) == bool(self.sag_plate):
            error_msg = """You have to specify either an Extracted cell or a
            Sample, but not both."""
            raise(ValidationError({"sag_plate_dilution": [error_msg, ],
                                   "extracted_cell": [error_msg, ]}))
        super(SAG, self).clean()

    class Meta:
        verbose_name = "SAG"
        verbose_name_plural = "SAGs"

    def __unicode__(self):
        return unicode(self.uid)

    @property
    def sample(self):
        if self.sag_plate:
            return self.sag_plate.sample
        elif self.sag_plate_dilution:
            return self.sag_plate_dilution.sample
        else:
            raise(Exception("Invalid object. Should belong to SAGPlate or "
                            "SAGPlateDilution"))

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [
            'id',
            'uid',
            'sag_plate',
            'sag_plate_dilution',
            'well',
            'concentration',
        ]


class DNAFromPureCulture(IndexByGroup):
    extracted_dna = models.ForeignKey(ExtractedDNA)
    concentration = models.DecimalField(u"Concentration (mol L\u207B\u00B9)",
                                        max_length=100, max_digits=10,
                                        decimal_places=5)
    date = models.DateTimeField(default=timezone.now, blank=True)
    uid = models.CharField("UID", max_length=30, unique=True, default="Automatically generated",
        help_text="UID consists of the sample UID followed by A_Z and count [01-99] i.e. 10Y31A_Z01")

    group_id_keyword = "extracted_dna__sample__id"
    character_list = ["%02d" % i for i in range(1, 100)]  # [01-99]

    objects = UIDManager()

    def natural_key(self):
        return self.uid

    @property
    def sample(self):
        return self.group

    @property
    def group(self):
        return self.extracted_dna.sample

    def save(self):
        """Stores UID on save"""
        if self.pk is None:
            self.index_by_group = self.calc_index_by_group()
            self.uid = self.group.uid + "A_Z" + self.index_to_naming_scheme()
        super(DNAFromPureCulture, self).save()

    def __unicode__(self):
        return unicode(self.uid)

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [
            'id',
            'uid',
            'extracted_dna',
            'concentration',
        ]

    class Meta:
        verbose_name = "DNA from pure culture"


class DNALibrary(StorablePhysicalObject, IndexByGroup):
    amplicon = models.ForeignKey(Amplicon, blank=True, null=True)
    metagenome = models.ForeignKey(Metagenome, blank=True, null=True)
    sag = models.ForeignKey(SAG, null=True, blank=True, verbose_name="SAG")
    pure_culture = models.ForeignKey(DNAFromPureCulture, blank=True, null=True)

    buffer = models.CharField(max_length=100)
    i7 = models.CharField(max_length=100)
    i5 = models.CharField(max_length=100)
    sample_name_on_platform = models.CharField(max_length=100, unique=True)
    concentration = models.DecimalField(u"Concentration (mol L\u207B\u00B9)",
                                        max_length=100, max_digits=10,
                                        decimal_places=5)

    protocol = models.ForeignKey(Protocol)
    date = models.DateTimeField(default=timezone.now, blank=True)
    uid = models.CharField("UID", max_length=30, unique=True, default="Automatically generated",
        help_text="UID consists of the UID of the Amplicon, Metagenome, DNAFromPureCulture or SAG followed by a character [A-Z] i.e. AMZNGA_Y01A")

    character_list = [chr(ord('A') + i) for i in range(26)]  # [A-Z]

    objects = UIDManager()

    def natural_key(self):
        return self.uid

    @property
    def dna_type(self):
        if self.amplicon:
            return "Amplicon"
        elif self.sag:
            return "SAG"
        elif self.pure_culture:
            return "Pure DNA"
        elif self.metagenome:
            return "Metagenome"
        else:
            raise(Exception("No DNA source specified."))

    @property
    def group_id_keyword(self):
        return {"Amplicon"  : "amplicon__id",
                "SAG"       : "sag__id",
                "Pure DNA"  : "pure_culture__id",
                "Metagenome": "metagenome__id"}[self.dna_type]

    @property
    def sample(self):
        return self.group.sample

    @property
    def group(self):
        return self.amplicon or self.sag or self.pure_culture or self.metagenome

    @property
    def barcode(self):
        return "DL:" + str(self.uid)

    def save(self):
        if sum((bool(self.amplicon),
                bool(self.metagenome),
                bool(self.sag),
                bool(self.pure_culture))) == 1:
            if self.pk is None:
                self.index_by_group = self.calc_index_by_group()
                self.uid = self.group.uid + self.index_to_naming_scheme()
            super(DNALibrary, self).save()
        else:
            raise(Exception("You have to specify a DNA source from either "
                            "Amplicon, Metagenome, SAG or Pure culture and not "
                            "more than one"))

    def clean(self):
        if sum((bool(self.amplicon),
                bool(self.metagenome),
                bool(self.sag),
                bool(self.pure_culture))) != 1:
            error_msg = """You have to specify a DNA source from either
            Amplicon, Metagenome, SAG or Pure culture and not more than one."""
            raise(ValidationError({"amplicon": [error_msg, ],
                                   "metagenome": [error_msg, ],
                                   "sag": [error_msg, ],
                                   "pure_culture": [error_msg, ],
                                   }))
        super(DNALibrary, self).clean()

    class Meta:
        verbose_name = "DNA library"
        verbose_name_plural = verbose_name[:-1] + "ies"

    def __unicode__(self):
        return unicode("%s") % (self.uid)

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [
            'id',
            'uid',
            'buffer',
            'i7',
            'i5',
            'sample_name_on_platform',
            'protocol',
            'container',
            'dna_type',
            'group',
        ]


class SequencingRun(models.Model):
    uid = models.CharField("UID", max_length=100, unique=True)
    sequencing_center = models.CharField(max_length=100)
    machine = models.CharField(max_length=100)
    report = models.CharField(max_length=100)
    folder = models.CharField(max_length=100)
    notes = models.TextField()
    dna_library = models.ManyToManyField(DNALibrary)
    protocol = models.ForeignKey(Protocol)
    date = models.DateTimeField(default=timezone.now, blank=True)

    objects = UIDManager()

    def natural_key(self):
        return self.uid

    def __unicode__(self):
        return unicode("%s") % (self.uid)

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [f.attname for f in self._meta.fields]


class ReadFile(models.Model):
    folder = models.CharField(max_length=100)
    filename = models.CharField(max_length=100)
    pair = models.PositiveIntegerField(choices=((1, 1), (2, 2)))
    lane = models.PositiveIntegerField()
    read_count = models.PositiveIntegerField()
    dna_library = models.ForeignKey(DNALibrary)
    sequencing_run = models.ForeignKey(SequencingRun)
    date = models.DateTimeField(default=timezone.now, blank=True)

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [f.attname for f in self._meta.fields]


class UserProfile(AbstractUser):
    #username = models.CharField(max_length=30, unique=True)
    date = models.DateTimeField(default=timezone.now, blank=True)

    #USERNAME_FIELD = 'username'
    #REQUIRED_FIELDS = ['']

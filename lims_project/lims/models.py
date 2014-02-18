from django.db import models
from django.contrib.auth.models import AbstractUser


class IndexByGroup(models.Model):
    def get_count_by_group(self):
        return self.__class__.objects.filter(**{self.group_id_keyword: self.group.id}).count()

    def get_max_by_group(self):
        return self.__class__.objects.filter(
            **{self.group_id_keyword: self.group.id}).aggregate(
            models.Max('index_by_group'))['index_by_group__max']

    def calc_index_by_group(self):
        if self.pk is None:
            index_by_group = self.get_count_by_group()
            if hasattr(self, 'character_list') \
              and index_by_group >= len(self.character_list):
                raise(Exception("Too many objects, only %i %s supported by "
                                "naming scheme" % (len(self.character_list),
                                                   self.__class__)))
            return index_by_group
        else:
            return self.index_by_group

    def save(self):
        if self.pk is None:
            self.index_by_group = self.calc_index_by_group()
        super(IndexByGroup, self).save()

    def index_to_naming_scheme(self):
        try:
            return self.character_list[self.index_by_group]
        except IndexError:
            raise(Exception("Too many objects, only %i %s supported by naming"
                            "scheme" % (len(self.character_list),
                                        self.__class__)))

    class Meta:
        abstract = True

    index_by_group = models.IntegerField(default="Automatically generated")


def property_verbose(description):
    """Make the function a property and give it a description. Normal property
    decoration does not work with short_description"""
    def property_verbose_inner(function):
        function.short_description = description
        return property(function)
    return property_verbose_inner


class Collaborator(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=100)
    email = models.EmailField()
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [
            'id',
            'first_name',
            'last_name',
            'institution',
            'address',
            'phone',
            'email',
            'notes',
        ]


class SampleType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return "%s" % (self.name)


class SampleLocation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return "%s" % (self.name)


class StorageLocation(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=False)

    def __unicode__(self):
        return "%s" % (self.name)


class Sample(models.Model):
    uid = models.CharField("UID", max_length=20, unique=True)

    collaborator = models.ForeignKey(Collaborator)
    sample_type = models.ForeignKey(SampleType)
    sample_location = models.ForeignKey(SampleLocation)
    storage_location = models.ForeignKey(StorageLocation, blank=True, null=True)

    temperature = models.DecimalField(u"Temperature \u00B0C", max_digits=10,
        decimal_places=2, blank=True, null=True)
    ph = models.DecimalField(" pH", max_digits=10, decimal_places=2, blank=True, null=True)
    salinity = models.DecimalField("Salinity unit(?))", max_digits=10, decimal_places=2, blank=True, null=True)
    depth = models.DecimalField("Depth (m)", max_digits=10, decimal_places=2, blank=True, null=True)
    gps = models.CharField("GPS", max_length=30, blank=True)
    shipping_method = models.CharField(max_length=30, blank=True)
    storage_medium = models.CharField(max_length=30, blank=True)
    date_received = models.DateField(blank=True)
    biosafety_level = models.IntegerField(
        choices=((1, 1), (2, 2), (3, 3), (4, 4)), blank=True, null=True)
    status = models.CharField(max_length=8,
        choices=(('new', 'new'), ('used', 'used'), ('finished', 'finished')), blank=True, null=True)
    notes = models.TextField(blank=True)

    @property
    def barcode(self):
        return "SA:" + str(self.uid)

    def __unicode__(self):
        return "%s" % (self.uid)

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
            'notes',
        ]


class Protocol(models.Model):
    name = models.CharField(max_length=30)
    revision = models.CharField(max_length=30)
    link = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return "%s" % (self.name)


class ExtractedCell(IndexByGroup):
    sample = models.ForeignKey(Sample)
    protocol = models.ForeignKey(Protocol)
    storage_location = models.ForeignKey(StorageLocation)
    notes = models.TextField(blank=True)

    group_id_keyword = "sample__id"

    @property
    def group(self):
        return self.sample

    @property
    def barcode(self):
        return "EC:%s" % str(self.uid)

    @property_verbose("UID")
    def uid(self):
        return "%s_%s" % (self.group.uid, self.index_by_group + 1)

    def __unicode__(self):
        return self.uid

    @property
    def preferred_ordering(self):
        return [
            'id',
            'sample',
            'protocol',
            'storage_location',
            'notes',
        ]


class ExtractedDNA(IndexByGroup):
    sample = models.ForeignKey(Sample, null=True, blank=True)
    protocol = models.ForeignKey(Protocol)
    storage_location = models.ForeignKey(StorageLocation)
    notes = models.TextField(blank=True)
    extracted_cell = models.ForeignKey(ExtractedCell, null=True, blank=True)

    @property
    def group_id_keyword(self):
        return "sample__id" if self.sample else "extracted_cell__sample__id"

    @property
    def group(self):
        return self.sample if self.sample else self.extracted_cell.sample

    @property
    def barcode(self):
        return "ED:" + str(self.uid)

    @property_verbose("UID")
    def uid(self):
        return "%s_%s" % (self.sample.uid, self.index_by_group + 1)

    def save(self):
        """Saves and checks whether either Sample or ExtractedCell is provided.
        Not both, because this makes it easier to change the Sample on an
        ExtractedCell for example. Otherwise you would have to change both this
        object and the Extracted Cell."""
        if bool(self.sample) != bool(self.extracted_cell):
            #if self.sample:
            #    sample = self.sample
            #else:
            #    sample = self.extracted_cell.sample
            super(ExtractedDNA, self).save()
        else:
            raise(Exception("You have to specify an Extracted cell or"
                            " a Sample, but not both."))

    class Meta:
        verbose_name = "Extracted DNA"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.uid

    @property
    def preferred_ordering(self):
        return [
            'id',
            'uid',
            'sample',
            'protocol',
            'storage_location',
            'notes',
            'extracted_cell',
        ]


class QPCR(models.Model):
    report = models.CharField(max_length=100)

    class Meta:
        verbose_name = "QPCR"
        verbose_name_plural = "QPCRs"

    def __unicode__(self):
        return self.report


class RTMDA(models.Model):
    report = models.CharField(max_length=100)

    class Meta:
        verbose_name = "RT-MDA kinetics"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.report


class SAGPlate(IndexByGroup):
    report = models.CharField(max_length=100)
    protocol = models.ForeignKey(Protocol)
    storage_location = models.ForeignKey(StorageLocation)
    notes = models.TextField(blank=True)
    extracted_cell = models.ForeignKey(ExtractedCell)
    rt_mda = models.ForeignKey(RTMDA)
    qpcr = models.ForeignKey(QPCR)

    group_id_keyword = "extracted_cell__sample__id"
    character_list = [chr(ord('A') + i) for i in range(26)]  # [A-Z]

    @property
    def sample(self):
        return self.group

    @property
    def group(self):
        return self.extracted_cell.sample

    @property
    def barcode(self):
        return "SP:" + str(self.uid)

    @property_verbose("UID")
    def uid(self):
        return self.extracted_cell.sample.uid + \
            self.index_to_naming_scheme()

    class Meta:
        verbose_name = "SAG plate"
        verbose_name_plural = verbose_name + "s"

    def __unicode__(self):
        return self.uid

    @property
    def preferred_ordering(self):
        return ['id',
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


class SAGPlateDilution(IndexByGroup):
    sag_plate = models.ForeignKey(SAGPlate)
    dilution = models.CharField(max_length=100)
    qpcr = models.ForeignKey(QPCR)

    group_id_keyword = "extracted_cell__sample__id"
    character_list = [chr(ord('a') + i) for i in range(26)] + range(10)  # [a-z0-9]

    @property
    def sample(self):
        return self.group

    @property
    def group(self):
        return self.sag_plate.extracted_cell.sample

    @property
    def barcode(self):
        return "SP:" + str(self.uid)

    @property_verbose("UID")
    def uid(self):
        return self.sag_plate.extracted_cell.sample.uid + \
            self.index_to_naming_scheme()

    class Meta:
        verbose_name = "SAG plate dilution"
        verbose_name_plural = verbose_name + "s"

    def __unicode__(self):
        return self.uid


class Metagenome(IndexByGroup):
    extracted_dna = models.ForeignKey(ExtractedDNA)
    diversity_report = models.CharField(max_length=100)

    group_id_keyword = "extracted_dna__sample__id"
    character_list = ["%02d" % i for i in range(1, 100)]  # [01-99]

    @property
    def sample(self):
        return self.group

    @property
    def group(self):
        return self.extracted_dna.sample

    @property_verbose("UID")
    def uid(self):
        return self.extracted_dna.sample.uid + "A_X" + \
            self.index_to_naming_scheme()

    def __unicode__(self):
        return self.uid

    @property
    def preferred_ordering(self):
        return ['id',
                'uid',
                'diversity_report',
        ]


class Primer(models.Model):
    sequence = models.TextField()
    storage_location = models.ForeignKey(StorageLocation)
    tmelt = models.DecimalField(u"tmelt (\u00B0C)", max_digits=10,
                                decimal_places=2)
    concentration = models.DecimalField(u"Concentration (mol L\u207B\u00B9)",
                                        max_length=100, max_digits=10,
                                        decimal_places=5)
    stock = models.PositiveIntegerField()


class Amplicon(IndexByGroup):
    extracted_dna = models.ForeignKey(ExtractedDNA)
    diversity_report = models.CharField(max_length=100)
    buffer = models.CharField(max_length=100)
    notes = models.TextField()
    primer = models.ManyToManyField(Primer)

    group_id_keyword = "extracted_dna__sample__id"
    character_list = ["%02d" % i for i in range(1, 100)]  # [01-99]

    @property
    def sample(self):
        return self.group

    @property
    def group(self):
        return self.extracted_dna.sample

    @property_verbose("UID")
    def uid(self):
        return self.extracted_dna.sample.uid + "A_Y" + \
            self.index_to_naming_scheme()

    def __unicode__(self):
        return self.uid


class SAG(models.Model):
    sag_plate = models.ForeignKey(SAGPlate, null=True)
    sag_plate_dilution = models.ForeignKey(SAGPlateDilution, null=True)
    well = models.CharField(max_length=3)
    concentration = models.DecimalField(u"Concentration (mol L\u207B\u00B9)",
                                        max_length=100, max_digits=10,
                                        decimal_places=5)

    def save(self):
        if sum((bool(self.sag_plate_dilution),
                bool(self.sag_plate))) == 1:
            super(SAG, self).save()
        else:
            raise(Exception("You have to specify either a SAGPlate or a "
                            "SAGPlateDilution and not both"))

    class Meta:
        verbose_name = "SAG"
        verbose_name_plural = "SAGs"

    @property_verbose("UID")
    def uid(self):
        sag_uid = self.sag_plate.uid if self.sag_plate else \
            self.sag_plate_dilution.uid
        return "%s_%s" % (sag_uid, self.well)

    def __unicode__(self):
        return self.uid

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


class PureCulture(IndexByGroup):
    extracted_dna = models.ForeignKey(ExtractedDNA)
    concentration = models.DecimalField(u"Concentration (mol L\u207B\u00B9)",
                                        max_length=100, max_digits=10,
                                        decimal_places=5)

    group_id_keyword = "extracted_dna__sample__id"
    character_list = ["%02d" % i for i in range(1, 100)]  # [01-99]

    @property
    def sample(self):
        return self.group

    @property
    def group(self):
        return self.extracted_dna.sample

    @property_verbose("UID")
    def uid(self):
        return self.extracted_dna.sample.uid + "A_Z" + \
            self.index_to_naming_scheme()

    def __unicode__(self):
        return self.uid

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [
            'id',
            'uid',
            'extracted_dna',
            'concentration',
        ]


class DNALibrary(IndexByGroup):
    amplicon = models.ForeignKey(Amplicon, blank=True, null=True)
    metagenome = models.ForeignKey(Metagenome, blank=True, null=True)
    sag = models.ForeignKey(SAG, null=True, blank=True, verbose_name="SAG")
    pure_culture = models.ForeignKey(PureCulture, blank=True, null=True)

    buffer = models.CharField(max_length=100)
    i7 = models.CharField(max_length=100)
    i5 = models.CharField(max_length=100)
    sample_name_on_platform = models.CharField(max_length=100, unique=True)

    #fastq_files
    protocol = models.ForeignKey(Protocol)
    storage_location = models.ForeignKey(StorageLocation)

    group_id_keyword = "extracted_cell__sample__id"
    character_list = [chr(ord('A') + i) for i in range(26)]  # [A-Z]

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
                "Metagenome": "metagenome__id",
               }[self.dna_type]

    @property
    def sample(self):
        return self.group.sample

    @property
    def group(self):
        return self.amplicon or self.sag or self.pure_culture or self.metagenome

    @property_verbose("UID")
    def uid(self):
        return self.group.uid + \
            self.index_to_naming_scheme()

    def save(self):
        if sum((bool(self.amplicon),
                bool(self.metagenome),
                bool(self.sag),
                bool(self.pure_culture))) == 1:
            super(DNALibrary, self).save()
        else:
            raise(Exception("You have to specify a DNA source from either "
                            "Amplicon, Metagenome, SAG or Pure culture and not "
                            "more than one"))

    class Meta:
        verbose_name = "DNA library"
        verbose_name_plural = verbose_name[:-1] + "ies"

    def __unicode__(self):
        return "%s" % (self.uid)

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
            'storage_location',
            'dna_type',
            'group',
        ]


class SequencingRun(models.Model):
    uid = models.CharField("UID", max_length=100, unique=True)
    date = models.DateField()
    sequencing_center = models.CharField(max_length=100)
    machine = models.CharField(max_length=100)
    report = models.CharField(max_length=100)
    folder = models.CharField(max_length=100)
    notes = models.TextField()
    dna_library = models.ManyToManyField(DNALibrary)

    protocol = models.ForeignKey(Protocol)

    def __unicode__(self):
        return "%s" % (self.uid)


class ReadFile(models.Model):
    folder = models.CharField(max_length=100)
    filename = models.CharField(max_length=100)
    pair = models.PositiveIntegerField(choices=((1, 1), (2, 2)))
    lane = models.PositiveIntegerField()
    read_count = models.PositiveIntegerField()
    dna_library = models.ForeignKey(DNALibrary)
    sequencing_run = models.ForeignKey(SequencingRun)

    @property
    def preferred_ordering(self):
        """Returns an ordered list of attribute names"""
        return [
            'id',
            'filename',
            'pair',
            'lane',
            'read_count',
            'dna_library',
            'sequencing_run',
        ]



class UserProfile(AbstractUser):
    fullname = models.CharField(max_length=30, unique=True)

    #USERNAME_FIELD = 'fullname'
    #REQUIRED_FIELDS = ['']

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

# Create your models here.
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

class SampleType(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(blank=False)

    def __unicode__(self):
        return "%s" % (self.name)

class SampleLocation(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(blank=False)

    def __unicode__(self):
        return "%s" % (self.name)

class StorageLocation(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(blank=False)

    def __unicode__(self):
        return "%s" % (self.name)

class Sample(models.Model):
    uid = models.CharField("UID", max_length=20, unique=True)

    collaborator = models.ForeignKey(Collaborator)
    sample_type = models.ForeignKey(SampleType)
    sample_location = models.ForeignKey(SampleLocation)
    storage_location = models.ForeignKey(StorageLocation)

    temperature = models.DecimalField(u"Temperature \u00B0C", max_digits=10,
        decimal_places=2)
    ph = models.DecimalField(" pH", max_digits=10, decimal_places=2)
    salinity = models.DecimalField("Salinity unit(?))", max_digits=10, decimal_places=2)
    depth = models.DecimalField("Depth (m)", max_digits=10, decimal_places=2)
    gps = models.CharField("GPS", max_length=30)
    shipping_method = models.CharField(max_length=30)
    storage_medium = models.CharField(max_length=30)
    date_received = models.DateField()
    biosafety_level = models.IntegerField(
        choices=((1, 1), (2, 2), (3, 3), (4, 4)))
    status = models.CharField(max_length=8,
        choices=(('new', 'new'), ('used', 'used'), ('finished','finished')))
    notes = models.TextField(blank=True)

    @property
    def barcode(self):
        return "SA:" + str(self.uid)

    def __unicode__(self):
        return "%s" % (self.uid)


class Protocol(models.Model):
    name = models.CharField(max_length=30)
    revision = models.CharField(max_length=30)
    link = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return "%s" % (self.name)

class ExtractedCell(models.Model):
    sample = models.ForeignKey(Sample)
    uid = models.CharField("UID", max_length=20, unique=True, editable=False)
    replicate_number = models.IntegerField(default="Automatically generated")
    protocol = models.ForeignKey(Protocol)
    storage_location = models.ForeignKey(StorageLocation)
    notes = models.TextField(blank=True)

    @property
    def barcode(self):
        return "EC:%s" % str(self.uid)

    def save(self):
        self.replicate_number = ExtractedCell.objects.filter(sample=self.sample.id).count() + 1
        self.uid = "%s_%s" % (self.sample.uid, self.replicate_number)
        super(ExtractedCell, self).save()

    def __unicode__(self):
        return self.uid

class ExtractedDNA(models.Model):
    sample = models.ForeignKey(Sample)
    uid = models.CharField("UID", max_length=20, unique=True, editable=False)
    replicate_number = models.IntegerField(default="Automatically generated")
    protocol = models.ForeignKey(Protocol)
    storage_location = models.ForeignKey(StorageLocation)
    notes = models.TextField(blank=True)
    extracted_cell = models.ForeignKey(ExtractedCell, null=True, blank=True)

    @property
    def barcode(self):
        return "ED:" + str(self.uid)

    def save(self):
        self.replicate_number = ExtractedDNA.objects.filter(sample=self.sample.id).count() + 1
        self.uid = "%s_%s" % (self.sample.uid, self.replicate_number)
        super(ExtractedDNA, self).save()

    class Meta:
        verbose_name = "Extracted DNA"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.uid

class QPCR(models.Model):
    report = models.CharField(max_length=100)

    class Meta:
        verbose_name = "QPCR"
        verbose_name_plural = "QPCRs"

class RTMDA(models.Model):
    report = models.CharField(max_length=100)

    class Meta:
        verbose_name = "RT-MDA kinetics"
        verbose_name_plural = verbose_name

class SAGPlate(models.Model):
    report = models.CharField(max_length=100)
    protocol = models.ForeignKey(Protocol)
    storage_location = models.ForeignKey(StorageLocation)
    notes = models.TextField()
    extracted_cell = models.ForeignKey(ExtractedCell)
    rt_mda = models.ForeignKey(RTMDA)
    qpcr = models.ForeignKey(QPCR)

    @property
    def barcode(self):
        return "SP:" + str(self.sample.id)

    class Meta:
        verbose_name = "SAG plate"
        verbose_name_plural = verbose_name + "s"

class SAGPlateDilution(models.Model):
    sag_plate = models.ForeignKey(SAGPlate)
    dilution = models.CharField(max_length=100)
    qpcr = models.ForeignKey(QPCR)

    class Meta:
        verbose_name = "SAG plate dilution"
        verbose_name_plural = verbose_name + "s"

class DNALibrary(models.Model):
    limit = models.Q(app_label = 'lims', model = 'amplicon') | \
            models.Q(app_label = 'lims', model = 'metagenome') | \
            models.Q(app_label = 'lims', model = 'sag') | \
            models.Q(app_label = 'lims', model = 'pureculture')
    content_type = models.ForeignKey(ContentType, limit_choices_to=limit)
    object_id = models.PositiveIntegerField(choices=(('5','5'),))
    current_object = generic.GenericForeignKey('content_type', 'object_id')

    buffer = models.CharField(max_length=100)
    i7 = models.CharField(max_length=100)
    i5 = models.CharField(max_length=100)
    sample_name_on_platform = models.CharField(max_length=100)

    #fastq_files
    protocol = models.ForeignKey(Protocol)
    storage_location = models.ForeignKey(StorageLocation)

    class Meta:
        verbose_name = "DNA library"
        verbose_name_plural = verbose_name[:-1] + "ies"

class SequencingRun(models.Model):
    date = models.DateField()
    machine = models.CharField(max_length=100)
    report = models.CharField(max_length=100)
    folder = models.CharField(max_length=100)
    notes = models.TextField()
    dna_library = models.ManyToManyField(DNALibrary)

    protocol = models.ForeignKey(Protocol)

class Metagenome(models.Model):
    extracted_dna = models.ForeignKey(ExtractedDNA)
    sample = models.ForeignKey(Sample)
    diversity_report = models.CharField(max_length=100)
    dna_library = generic.GenericRelation(DNALibrary)

class Primer(models.Model):
    sequence = models.TextField()
    storage_location = models.ForeignKey(StorageLocation)
    tmelt = models.DecimalField(u"tmelt \u00B0C", max_digits=10,
                                decimal_places=2)
    concentration = models.CharField(max_length=100)
    stock = models.PositiveIntegerField()

class Amplicon(models.Model):
    extracted_dna = models.ForeignKey(ExtractedDNA)
    sample = models.ForeignKey(Sample)
    diversity_report = models.CharField(max_length=100)
    buffer = models.CharField(max_length=100)
    notes = models.TextField()
    primer = models.ManyToManyField(Primer)
    dna_library = generic.GenericRelation(DNALibrary)

class SAG(models.Model):
    sag_plate_dilution = models.ForeignKey(SAGPlateDilution)
    well = models.CharField(max_length=3)
    concentration = models.CharField(max_length=100)
    dna_library = generic.GenericRelation(DNALibrary)

    class Meta:
        verbose_name = "SAG"
        verbose_name_plural = "SAGs"

class PureCulture(models.Model):
    extracted_dna = models.ForeignKey(ExtractedDNA)
    concentration = models.CharField(max_length=100)
    dna_library = generic.GenericRelation(DNALibrary)

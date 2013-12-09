from django.db import models

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
    description = models.TextField()

    def __unicode__(self):
        return "%s %s" % (self.name, self.description)

class SampleLocation(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()

class StorageLocation(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()

class Sample(models.Model):
    id = models.CharField("ID", max_length=20, primary_key=True)

    collaborator = models.ForeignKey(Collaborator)
    sample_type = models.ForeignKey(SampleType)
    sample_location = models.ForeignKey(SampleLocation)
    storage_location = models.ForeignKey(StorageLocation)

    temperature = models.DecimalField(u"Temperature \u00B0C", max_digits=3,
        decimal_places=2)
    ph = models.DecimalField(" pH", max_digits=3, decimal_places=2)
    salinity = models.DecimalField("Salinity unit(?))", max_digits=3, decimal_places=2)
    depth = models.DecimalField(max_digits=3, decimal_places=2)
    gps = models.CharField("GPS", max_length=30)
    shipping_method = models.CharField(max_length=30)
    storage_medium = models.CharField(max_length=30)
    date_received = models.DateField()
    biosafety_level = models.IntegerField(
        choices=((1, 1), (2, 2), (3, 3), (4, 4)))
    status = models.CharField(max_length=8,
        choices=(('new', 'new'), ('used', 'used'), ('finished','finished')))
    notes = models.TextField()

    @property
    def barcode(self):
        return "SA:" + str(self.id)

class Protocol(models.Model):
    info = models.TextField()
    revision = models.CharField(max_length=30)
    link = models.CharField(max_length=100)

class ExtractedCell(models.Model):
    sample = models.ForeignKey(Sample)
    replicate_number = models.IntegerField()
    protocol = models.ForeignKey(Protocol)
    storage_location = models.ForeignKey(StorageLocation)
    notes = models.TextField()

    @property
    def barcode(self):
        return "EC:" + str(self.sample.id)

class ExtractedDNA(models.Model):
    sample = models.ForeignKey(Sample)
    replicate_number = models.IntegerField()
    protocol = models.ForeignKey(Protocol)
    storage_location = models.ForeignKey(StorageLocation)
    notes = models.TextField()
    extracted_cell = models.ForeignKey(ExtractedCell)

    @property
    def barcode(self):
        return "ED:" + str(self.sample.id)

class QPCR(models.Model):
    report = models.CharField(max_length=100)

class RTMDA(models.Model):
    report = models.CharField(max_length=100)

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

class SAGPlateDilution(models.Model):
    sag_plate = models.ForeignKey(SAGPlate)
    dilution = models.CharField(max_length=100)
    qpcr = models.ForeignKey(QPCR)

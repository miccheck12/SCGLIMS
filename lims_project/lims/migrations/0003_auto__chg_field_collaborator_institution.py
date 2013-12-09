# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Collaborator.institution'
        db.alter_column(u'lims_collaborator', 'institution', self.gf('django.db.models.fields.CharField')(max_length=100))

    def backwards(self, orm):

        # Changing field 'Collaborator.institution'
        db.alter_column(u'lims_collaborator', 'institution', self.gf('django.db.models.fields.TextField')())

    models = {
        u'lims.collaborator': {
            'Meta': {'object_name': 'Collaborator'},
            'address': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'lims.sample': {
            'Meta': {'object_name': 'Sample'},
            'biosafety_level': ('django.db.models.fields.IntegerField', [], {}),
            'collaborator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lims.Collaborator']"}),
            'date_received': ('django.db.models.fields.DateField', [], {}),
            'depth': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '2'}),
            'gps': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {}),
            'ph': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '2'}),
            'salinity': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '2'}),
            'sample_location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lims.SampleLocation']"}),
            'sample_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lims.SampleType']"}),
            'shipping_method': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'storage_location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['lims.StorageLocation']"}),
            'storage_medium': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'temperature': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '2'})
        },
        u'lims.samplelocation': {
            'Meta': {'object_name': 'SampleLocation'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'lims.sampletype': {
            'Meta': {'object_name': 'SampleType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'lims.storagelocation': {
            'Meta': {'object_name': 'StorageLocation'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['lims']
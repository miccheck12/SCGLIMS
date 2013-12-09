# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Collaborator'
        db.create_table(u'lims_collaborator', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.TextField')()),
            ('last_name', self.gf('django.db.models.fields.TextField')()),
            ('institution', self.gf('django.db.models.fields.TextField')()),
            ('address', self.gf('django.db.models.fields.TextField')()),
            ('phone', self.gf('django.db.models.fields.TextField')()),
            ('email', self.gf('django.db.models.fields.TextField')()),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'lims', ['Collaborator'])

        # Adding model 'SampleType'
        db.create_table(u'lims_sampletype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'lims', ['SampleType'])

        # Adding model 'SampleLocation'
        db.create_table(u'lims_samplelocation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'lims', ['SampleLocation'])

        # Adding model 'StorageLocation'
        db.create_table(u'lims_storagelocation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'lims', ['StorageLocation'])

        # Adding model 'Sample'
        db.create_table(u'lims_sample', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=20, primary_key=True)),
            ('collaborator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lims.Collaborator'])),
            ('sample_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lims.SampleType'])),
            ('sample_location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lims.SampleLocation'])),
            ('storage_location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lims.StorageLocation'])),
            ('temperature', self.gf('django.db.models.fields.DecimalField')(max_digits=3, decimal_places=2)),
            ('ph', self.gf('django.db.models.fields.DecimalField')(max_digits=3, decimal_places=2)),
            ('salinity', self.gf('django.db.models.fields.DecimalField')(max_digits=3, decimal_places=2)),
            ('depth', self.gf('django.db.models.fields.DecimalField')(max_digits=3, decimal_places=2)),
            ('gps', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('shipping_method', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('storage_medium', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('date_received', self.gf('django.db.models.fields.DateField')()),
            ('biosafety_level', self.gf('django.db.models.fields.IntegerField')()),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('notes', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'lims', ['Sample'])


    def backwards(self, orm):
        # Deleting model 'Collaborator'
        db.delete_table(u'lims_collaborator')

        # Deleting model 'SampleType'
        db.delete_table(u'lims_sampletype')

        # Deleting model 'SampleLocation'
        db.delete_table(u'lims_samplelocation')

        # Deleting model 'StorageLocation'
        db.delete_table(u'lims_storagelocation')

        # Deleting model 'Sample'
        db.delete_table(u'lims_sample')


    models = {
        u'lims.collaborator': {
            'Meta': {'object_name': 'Collaborator'},
            'address': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.TextField', [], {}),
            'first_name': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.TextField', [], {}),
            'last_name': ('django.db.models.fields.TextField', [], {}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'phone': ('django.db.models.fields.TextField', [], {})
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
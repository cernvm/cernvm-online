# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Cluster'
        db.create_table(u'rest_api_cluster', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pin', self.gf('django.db.models.fields.CharField')(unique=True, max_length=12, blank=True)),
            ('creation_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'rest_api', ['Cluster'])

        # Adding model 'ClusterKeyValue'
        db.create_table(u'rest_api_clusterkeyvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(related_name='key_value_elements', to=orm['rest_api.Cluster'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal(u'rest_api', ['ClusterKeyValue'])


    def backwards(self, orm):
        # Deleting model 'Cluster'
        db.delete_table(u'rest_api_cluster')

        # Deleting model 'ClusterKeyValue'
        db.delete_table(u'rest_api_clusterkeyvalue')


    models = {
        u'rest_api.cluster': {
            'Meta': {'object_name': 'Cluster'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12', 'blank': 'True'})
        },
        u'rest_api.clusterkeyvalue': {
            'Meta': {'object_name': 'ClusterKeyValue'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'key_value_elements'", 'to': u"orm['rest_api.Cluster']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['rest_api']
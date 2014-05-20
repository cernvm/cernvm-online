# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'ClusterDefinition.ec2_json'
        db.delete_column(u'cluster_clusterdefinition', 'ec2_json')

        # Deleting field 'ClusterDefinition.elastiq_json'
        db.delete_column(u'cluster_clusterdefinition', 'elastiq_json')

        # Deleting field 'ClusterDefinition.quota_json'
        db.delete_column(u'cluster_clusterdefinition', 'quota_json')

        # Deleting field 'ClusterDefinition.additional_params_json'
        db.delete_column(u'cluster_clusterdefinition', 'additional_params_json')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'ClusterDefinition.ec2_json'
        raise RuntimeError("Cannot reverse this migration. 'ClusterDefinition.ec2_json' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'ClusterDefinition.ec2_json'
        db.add_column(u'cluster_clusterdefinition', 'ec2_json',
                      self.gf('django.db.models.fields.TextField')(),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'ClusterDefinition.elastiq_json'
        raise RuntimeError("Cannot reverse this migration. 'ClusterDefinition.elastiq_json' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'ClusterDefinition.elastiq_json'
        db.add_column(u'cluster_clusterdefinition', 'elastiq_json',
                      self.gf('django.db.models.fields.TextField')(),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'ClusterDefinition.quota_json'
        raise RuntimeError("Cannot reverse this migration. 'ClusterDefinition.quota_json' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'ClusterDefinition.quota_json'
        db.add_column(u'cluster_clusterdefinition', 'quota_json',
                      self.gf('django.db.models.fields.TextField')(),
                      keep_default=False)

        # Adding field 'ClusterDefinition.additional_params_json'
        db.add_column(u'cluster_clusterdefinition', 'additional_params_json',
                      self.gf('django.db.models.fields.TextField')(default='{}'),
                      keep_default=False)


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'cluster.clusterdefinition': {
            'Meta': {'object_name': 'ClusterDefinition'},
            'deployable_context': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['context.ContextStorage']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master_context': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'master_context'", 'to': u"orm['context.ContextDefinition']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'worker_context': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'worker_context'", 'to': u"orm['context.ContextDefinition']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'context.contextdefinition': {
            'Meta': {'object_name': 'ContextDefinition'},
            'abstract': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'checksum': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'from_abstract': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'inherited': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'public': ('django.db.models.fields.BooleanField', [], {})
        },
        u'context.contextstorage': {
            'Meta': {'object_name': 'ContextStorage'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'})
        }
    }

    complete_apps = ['cluster']
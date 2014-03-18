# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ClusterDefinition'
        db.create_table(u'cluster_clusterdefinition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'cluster', ['ClusterDefinition'])

        # Adding model 'ServiceOffering'
        db.create_table(u'cluster_serviceoffering', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal(u'cluster', ['ServiceOffering'])

        # Adding model 'DiskOffering'
        db.create_table(u'cluster_diskoffering', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal(u'cluster', ['DiskOffering'])

        # Adding model 'NetworkOffering'
        db.create_table(u'cluster_networkoffering', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=16, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal(u'cluster', ['NetworkOffering'])

        # Adding model 'Template'
        db.create_table(u'cluster_template', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal(u'cluster', ['Template'])

        # Adding model 'ServiceDefinition'
        db.create_table(u'cluster_servicedefinition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.ClusterDefinition'])),
            ('service_offering', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.ServiceOffering'])),
            ('disk_offering', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.DiskOffering'], null=True, blank=True)),
            ('network_offering', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.NetworkOffering'], null=True, blank=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cluster.Template'])),
            ('context', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['context.ContextDefinition'])),
            ('service_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('order', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('min_instances', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'cluster', ['ServiceDefinition'])


    def backwards(self, orm):
        # Deleting model 'ClusterDefinition'
        db.delete_table(u'cluster_clusterdefinition')

        # Deleting model 'ServiceOffering'
        db.delete_table(u'cluster_serviceoffering')

        # Deleting model 'DiskOffering'
        db.delete_table(u'cluster_diskoffering')

        # Deleting model 'NetworkOffering'
        db.delete_table(u'cluster_networkoffering')

        # Deleting model 'Template'
        db.delete_table(u'cluster_template')

        # Deleting model 'ServiceDefinition'
        db.delete_table(u'cluster_servicedefinition')


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
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'})
        },
        u'cluster.diskoffering': {
            'Meta': {'object_name': 'DiskOffering'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16', 'db_index': 'True'})
        },
        u'cluster.networkoffering': {
            'Meta': {'object_name': 'NetworkOffering'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16', 'db_index': 'True'})
        },
        u'cluster.servicedefinition': {
            'Meta': {'object_name': 'ServiceDefinition'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cluster.ClusterDefinition']"}),
            'context': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['context.ContextDefinition']"}),
            'disk_offering': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cluster.DiskOffering']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_instances': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'network_offering': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cluster.NetworkOffering']", 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'service_offering': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cluster.ServiceOffering']"}),
            'service_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cluster.Template']"}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'})
        },
        u'cluster.serviceoffering': {
            'Meta': {'object_name': 'ServiceOffering'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16', 'db_index': 'True'})
        },
        u'cluster.template': {
            'Meta': {'object_name': 'Template'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'})
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
        }
    }

    complete_apps = ['cluster']
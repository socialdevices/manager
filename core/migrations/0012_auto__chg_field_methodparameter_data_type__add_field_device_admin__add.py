# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'MethodParameter.data_type'
        db.alter_column('core_methodparameter', 'data_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.DataType'], null=True, on_delete=models.SET_NULL))
        # Adding field 'Device.admin'
        db.add_column('core_device', 'admin',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='admin_device_set', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Device.owner'
        db.add_column('core_device', 'owner',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='owner_device_set', null=True, to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Device.type'
        db.add_column('core_device', 'type',
                      self.gf('django.db.models.fields.CharField')(default='NO', max_length=2),
                      keep_default=False)


        # Changing field 'Method.return_data_type'
        db.alter_column('core_method', 'return_data_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.DataType'], null=True, on_delete=models.SET_NULL))

    def backwards(self, orm):

        # Changing field 'MethodParameter.data_type'
        db.alter_column('core_methodparameter', 'data_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.DataType'], null=True))
        # Deleting field 'Device.admin'
        db.delete_column('core_device', 'admin_id')

        # Deleting field 'Device.owner'
        db.delete_column('core_device', 'owner_id')

        # Deleting field 'Device.type'
        db.delete_column('core_device', 'type')


        # Changing field 'Method.return_data_type'
        db.alter_column('core_method', 'return_data_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.DataType'], null=True))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.action': {
            'Meta': {'object_name': 'Action'},
            'action_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'precondition_expression': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.actiondevice': {
            'Meta': {'unique_together': "(('action', 'name'), ('action', 'parameter_position'))", 'object_name': 'ActionDevice'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Action']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interfaces': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Interface']", 'through': "orm['core.ActionDeviceInterface']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parameter_position': ('django.db.models.fields.SmallIntegerField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.actiondeviceinterface': {
            'Meta': {'unique_together': "(('action_device', 'interface'),)", 'object_name': 'ActionDeviceInterface'},
            'action_device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.ActionDevice']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Interface']"})
        },
        'core.actionpreconditionmethod': {
            'Meta': {'unique_together': "(('action', 'expression_position'),)", 'object_name': 'ActionPreconditionMethod'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Action']"}),
            'action_device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.ActionDevice']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expression_position': ('django.db.models.fields.SmallIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Method']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.datatype': {
            'Meta': {'object_name': 'DataType'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.device': {
            'Meta': {'object_name': 'Device'},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admin_device_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interfaces': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Interface']", 'through': "orm['core.DeviceInterface']", 'symmetrical': 'False'}),
            'is_reserved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mac_address': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '17'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner_device_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'NO'", 'max_length': '2'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.deviceinterface': {
            'Meta': {'unique_together': "(('device', 'interface'),)", 'object_name': 'DeviceInterface'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Interface']"})
        },
        'core.interface': {
            'Meta': {'object_name': 'Interface'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.method': {
            'Meta': {'unique_together': "(('name', 'interface'),)", 'object_name': 'Method'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Interface']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'return_data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DataType']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.methodparameter': {
            'Meta': {'unique_together': "(('name', 'method'),)", 'object_name': 'MethodParameter'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DataType']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Method']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.schedule': {
            'Meta': {'object_name': 'Schedule'},
            'actions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Action']", 'through': "orm['core.ScheduleAction']", 'symmetrical': 'False'}),
            'configuration_model_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'configuration_model_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'schedule_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'trigger': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Trigger']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.scheduleaction': {
            'Meta': {'unique_together': "(('schedule', 'action'),)", 'object_name': 'ScheduleAction'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Action']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Schedule']"}),
            'trigger_device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.ActionDevice']", 'null': 'True', 'blank': 'True'})
        },
        'core.statevalue': {
            'Meta': {'unique_together': "(('device', 'method'),)", 'object_name': 'StateValue'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Method']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'core.statevalueargument': {
            'Meta': {'unique_together': "(('state_value', 'method_parameter'),)", 'object_name': 'StateValueArgument'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method_parameter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.MethodParameter']"}),
            'state_value': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.StateValue']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'core.trigger': {
            'Meta': {'object_name': 'Trigger'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Method']", 'unique': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['core']
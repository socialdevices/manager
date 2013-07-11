# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Interface'
        db.create_table('core_interface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('interface_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Interface'])

        # Adding model 'Device'
        db.create_table('core_device', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('mac_address', self.gf('django.db.models.fields.CharField')(unique=True, max_length=17)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_reserved', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('core', ['Device'])

        # Adding model 'DeviceInterface'
        db.create_table('core_deviceinterface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Device'])),
            ('interface', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Interface'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('core', ['DeviceInterface'])

        # Adding unique constraint on 'DeviceInterface', fields ['device', 'interface']
        db.create_unique('core_deviceinterface', ['device_id', 'interface_id'])

        # Adding model 'DataType'
        db.create_table('core_datatype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
        ))
        db.send_create_signal('core', ['DataType'])

        # Adding model 'Method'
        db.create_table('core_method', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('interface', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Interface'])),
            ('return_data_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.DataType'], null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Method'])

        # Adding unique constraint on 'Method', fields ['name', 'interface']
        db.create_unique('core_method', ['name', 'interface_id'])

        # Adding model 'MethodParameter'
        db.create_table('core_methodparameter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('method', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Method'])),
            ('data_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.DataType'], null=True, blank=True)),
        ))
        db.send_create_signal('core', ['MethodParameter'])

        # Adding unique constraint on 'MethodParameter', fields ['name', 'method']
        db.create_unique('core_methodparameter', ['name', 'method_id'])

        # Adding model 'StateValue'
        db.create_table('core_statevalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Device'])),
            ('method', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Method'])),
        ))
        db.send_create_signal('core', ['StateValue'])

        # Adding unique constraint on 'StateValue', fields ['device', 'method']
        db.create_unique('core_statevalue', ['device_id', 'method_id'])

        # Adding model 'Action'
        db.create_table('core_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('precondition_expression', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('action_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Action'])

        # Adding model 'Trigger'
        db.create_table('core_trigger', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('method', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Method'])),
        ))
        db.send_create_signal('core', ['Trigger'])

        # Adding unique constraint on 'Trigger', fields ['method', 'value']
        db.create_unique('core_trigger', ['method_id', 'value'])

        # Adding model 'Schedule'
        db.create_table('core_schedule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('configuration_model_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('configuration_model_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('schedule_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('trigger', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Trigger'])),
        ))
        db.send_create_signal('core', ['Schedule'])

        # Adding model 'ScheduleAction'
        db.create_table('core_scheduleaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('schedule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Schedule'])),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Action'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('core', ['ScheduleAction'])

        # Adding unique constraint on 'ScheduleAction', fields ['schedule', 'action']
        db.create_unique('core_scheduleaction', ['schedule_id', 'action_id'])

        # Adding model 'ActionDevice'
        db.create_table('core_actiondevice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('parameter_position', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Action'])),
        ))
        db.send_create_signal('core', ['ActionDevice'])

        # Adding unique constraint on 'ActionDevice', fields ['action', 'parameter_position']
        db.create_unique('core_actiondevice', ['action_id', 'parameter_position'])

        # Adding model 'ActionDeviceInterface'
        db.create_table('core_actiondeviceinterface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.ActionDevice'])),
            ('interface', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Interface'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('core', ['ActionDeviceInterface'])

        # Adding unique constraint on 'ActionDeviceInterface', fields ['action_device', 'interface']
        db.create_unique('core_actiondeviceinterface', ['action_device_id', 'interface_id'])

        # Adding model 'ActionPreconditionMethod'
        db.create_table('core_actionpreconditionmethod', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('expression_position', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Action'])),
            ('action_device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.ActionDevice'])),
            ('method', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Method'])),
        ))
        db.send_create_signal('core', ['ActionPreconditionMethod'])

        # Adding unique constraint on 'ActionPreconditionMethod', fields ['action', 'expression_position']
        db.create_unique('core_actionpreconditionmethod', ['action_id', 'expression_position'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'ActionPreconditionMethod', fields ['action', 'expression_position']
        db.delete_unique('core_actionpreconditionmethod', ['action_id', 'expression_position'])

        # Removing unique constraint on 'ActionDeviceInterface', fields ['action_device', 'interface']
        db.delete_unique('core_actiondeviceinterface', ['action_device_id', 'interface_id'])

        # Removing unique constraint on 'ActionDevice', fields ['action', 'parameter_position']
        db.delete_unique('core_actiondevice', ['action_id', 'parameter_position'])

        # Removing unique constraint on 'ScheduleAction', fields ['schedule', 'action']
        db.delete_unique('core_scheduleaction', ['schedule_id', 'action_id'])

        # Removing unique constraint on 'Trigger', fields ['method', 'value']
        db.delete_unique('core_trigger', ['method_id', 'value'])

        # Removing unique constraint on 'StateValue', fields ['device', 'method']
        db.delete_unique('core_statevalue', ['device_id', 'method_id'])

        # Removing unique constraint on 'MethodParameter', fields ['name', 'method']
        db.delete_unique('core_methodparameter', ['name', 'method_id'])

        # Removing unique constraint on 'Method', fields ['name', 'interface']
        db.delete_unique('core_method', ['name', 'interface_id'])

        # Removing unique constraint on 'DeviceInterface', fields ['device', 'interface']
        db.delete_unique('core_deviceinterface', ['device_id', 'interface_id'])

        # Deleting model 'Interface'
        db.delete_table('core_interface')

        # Deleting model 'Device'
        db.delete_table('core_device')

        # Deleting model 'DeviceInterface'
        db.delete_table('core_deviceinterface')

        # Deleting model 'DataType'
        db.delete_table('core_datatype')

        # Deleting model 'Method'
        db.delete_table('core_method')

        # Deleting model 'MethodParameter'
        db.delete_table('core_methodparameter')

        # Deleting model 'StateValue'
        db.delete_table('core_statevalue')

        # Deleting model 'Action'
        db.delete_table('core_action')

        # Deleting model 'Trigger'
        db.delete_table('core_trigger')

        # Deleting model 'Schedule'
        db.delete_table('core_schedule')

        # Deleting model 'ScheduleAction'
        db.delete_table('core_scheduleaction')

        # Deleting model 'ActionDevice'
        db.delete_table('core_actiondevice')

        # Deleting model 'ActionDeviceInterface'
        db.delete_table('core_actiondeviceinterface')

        # Deleting model 'ActionPreconditionMethod'
        db.delete_table('core_actionpreconditionmethod')


    models = {
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
            'Meta': {'unique_together': "(('action', 'parameter_position'),)", 'object_name': 'ActionDevice'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Action']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interfaces': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Interface']", 'through': "orm['core.ActionDeviceInterface']", 'symmetrical': 'False'}),
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
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interfaces': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Interface']", 'through': "orm['core.DeviceInterface']", 'symmetrical': 'False'}),
            'is_reserved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mac_address': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '17'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
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
            'return_data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DataType']", 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'core.methodparameter': {
            'Meta': {'unique_together': "(('name', 'method'),)", 'object_name': 'MethodParameter'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DataType']", 'null': 'True', 'blank': 'True'}),
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
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Schedule']"})
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
        'core.trigger': {
            'Meta': {'unique_together': "(('method', 'value'),)", 'object_name': 'Trigger'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Method']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['core']

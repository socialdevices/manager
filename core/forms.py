from core.clients import MirriClient, MirriConnectionError, MirriTimeoutError, \
    MirriNotFoundError
from core.models import Interface, Action, ActionPreconditionMethod, Method, \
    Schedule, Trigger, ActionDevice, ActionDeviceInterface, ScheduleAction, \
    MethodParameter, Device, ActionParameter
from core.parsers import InterfaceParser, ActionParser, ScheduleParser, \
    InterfaceParseError, ActionParseError, ScheduleParseError
from django import forms
from django.db import transaction
from django.utils import simplejson
from events.event import EventHandler
import logging

logger = logging.getLogger(__name__)


class UploadFileForm(forms.Form):
    file = forms.FileField(required=True)


class UploadInterfaceFileForm(UploadFileForm):

    def clean_file(self):
        file = self.cleaned_data['file']
        interface_code = file.read()
        file.seek(0)
        parser = InterfaceParser()

        interface = []
        try:
            interface = parser.parse(interface_code)
        except SyntaxError, e:
            raise forms.ValidationError('File %s contains syntax errors (line %s, col %s): %s' % (file.name, e.lineno, e.offset, e.text))
        except InterfaceParseError, e:
            raise forms.ValidationError('Interface parse error in file %s: %s' % (file.name, e))
        except Exception, e:
            raise forms.ValidationError('An undefined error occurred while parsing file %s. Please send the file to the administrators.' % file.name)

        if Interface.objects.filter(name=interface['interface_name']).exists():
            raise forms.ValidationError('Interface %s already exists.' % interface['interface_name'])

        return file

    def save(self):
        interface_code = self.cleaned_data['file'].read()
        parser = InterfaceParser()

        interface = parser.parse(interface_code)

        with transaction.commit_on_success():
            i = Interface(name=interface['interface_name'], interface_file=self.cleaned_data['file'])
            i.save()

            for method in interface['precondition_methods']:
                m = Method(name=method['method_name'], interface=i)
                m.save()

                for parameter in method['parameters']:
                    mp = MethodParameter(method=m, name=parameter)
                    mp.save()

            for trigger in interface['trigger_methods']:
                m = Method.objects.get(interface__name=interface['interface_name'], name=trigger)

                t = Trigger(method=m)
                t.save()

            # Send file to Mirri
            event_handler = EventHandler()
            try:
                client = MirriClient()
                client.upload_interface_file(interface['interface_name'], self.cleaned_data['file'])
            except (MirriConnectionError, MirriTimeoutError, MirriNotFoundError), e:
                logger.error('Interface file %s could not be posted to Mirri: %s' % (self.cleaned_data['file'].name, e))
                event_handler.add_event('Interface file %s could not be posted to Mirri: %s' % (self.cleaned_data['file'].name, e))
            else:
                logger.debug('Interface file %s posted to Mirri' % self.cleaned_data['file'].name)
                event_handler.add_event('Interface file %s posted to Mirri' % self.cleaned_data['file'].name)


class UploadActionFileForm(UploadFileForm):

    def clean_file(self):
        file = self.cleaned_data['file']
        action_code = file.read()
        file.seek(0)
        parser = ActionParser()

        action = []
        try:
            action = parser.parse(action_code)
        except SyntaxError, e:
            raise forms.ValidationError('File %s contains syntax errors (line %s, col %s): %s' % (file.name, e.lineno, e.offset, e.text))
        except ActionParseError, e:
            raise forms.ValidationError('Action parse error in file %s: %s' % (file.name, e))
        except Exception, e:
            raise forms.ValidationError('An undefined error occurred while parsing file %s. Please send the file to the administrators.' % file.name)

        if Action.objects.filter(name=action['action_name']).exists():
            raise forms.ValidationError('Action %s already exists.' % action['action_name'])

        for device in action['devices'].values():
            for interface_name in device['interfaces']:
                if not Interface.objects.filter(name=interface_name).exists():
                    raise forms.ValidationError('Interface %s does not exist.' % interface_name)

        for replacement in action['precondition_replacements']:
            if not Method.objects.filter(name=replacement['method'], interface__name=replacement['interface']).exists():
                raise forms.ValidationError('Method %s does not exist for interface %s.' % (replacement['method'], replacement['interface']))

        return file

    def save(self):
        action_code = self.cleaned_data['file'].read()
        parser = ActionParser()

        action = parser.parse(action_code)

        with transaction.commit_on_success():
            a = Action(name=action['action_name'], precondition_expression=action['precondition_expression'], action_file=self.cleaned_data['file'])
            a.save()

            for parameter in action['parameters']:
                ap = ActionParameter(action=a, name=parameter['name'], parameter_position=parameter['position'])
                ap.save()

            action_devices = {}

            for key, device in action['devices'].items():
                ad = ActionDevice(action=a, name=key, parameter_position=device['parameter_position'])
                ad.save()

                action_devices[key] = ad

                for interface_name in device['interfaces']:

                    i = Interface.objects.get(name=interface_name)

                    adi = ActionDeviceInterface(action_device=ad, interface=i)
                    adi.save()

            for position, replacement in enumerate(action['precondition_replacements']):

                apm = ActionPreconditionMethod(expression_position=position, action=a, action_device=action_devices[replacement['device']])

                m = Method.objects.get(name=replacement['method'], interface__name=replacement['interface'])

                apm.method = m
                apm.save()

            # Send file to Mirri
            event_handler = EventHandler()
            try:
                client = MirriClient()
                client.upload_action_file(self.cleaned_data['file'])
            except (MirriConnectionError, MirriTimeoutError, MirriNotFoundError), e:
                logger.error('Action file %s could not be posted to Mirri: %s' % (self.cleaned_data['file'].name, e))
                event_handler.add_event('Action file %s could not be posted to Mirri: %s' % (self.cleaned_data['file'].name, e))
            else:
                logger.debug('Action file %s posted to Mirri' % self.cleaned_data['file'].name)
                event_handler.add_event('Action file %s posted to Mirri' % self.cleaned_data['file'].name)


class UploadScheduleFileForm(UploadFileForm):

    def clean_file(self):
        file = self.cleaned_data['file']
        schedule_code = file.read()
        file.seek(0)
        parser = ScheduleParser()

        schedule = []
        try:
            schedule = parser.parse(schedule_code)
        except SyntaxError, e:
            raise forms.ValidationError('File %s contains syntax errors (line %s, col %s): %s' % (file.name, e.lineno, e.offset, e.text))
        except ScheduleParseError, e:
            raise forms.ValidationError('Schedule parse error in file %s: %s' % (file.name, e))
        except Exception, e:
            raise forms.ValidationError('An undefined error occurred while parsing file %s. Please send the file to the administrators.' % file.name)

        if Schedule.objects.filter(name=schedule['schedule_name']).exists():
            raise forms.ValidationError('Schedule %s already exists.' % schedule['schedule_name'])

        if not Trigger.objects.filter(method__name=schedule['trigger_method'], method__interface__name=schedule['trigger_interface']).exists():
            raise forms.ValidationError('Trigger method %s does not exist for interface %s.' % (schedule['trigger_method'], schedule['trigger_interface']))

        for action in schedule['actions']:
            if not Action.objects.filter(name=action['action_name']).exists():
                raise forms.ValidationError('Action %s does not exist.' % action['action_name'])

            if action['trigger_from'] != None and not ActionDevice.objects.filter(action__name=action['action_name'], parameter_position=action['trigger_from']).exists():
                raise forms.ValidationError('Trigger from position %s does not correspond to any valid action device position in action %s.' % (action['trigger_from'], action['action_name']))

        return file

    def save(self):
        schedule_code = self.cleaned_data['file'].read()
        parser = ScheduleParser()

        schedule = parser.parse(schedule_code)

        with transaction.commit_on_success():
            t = Trigger.objects.get(method__name=schedule['trigger_method'], method__interface__name=schedule['trigger_interface'])

            s = Schedule(trigger=t, name=schedule['schedule_name'], schedule_file=self.cleaned_data['file'])
            s.save()

            for action in schedule['actions']:
                a = Action.objects.get(name=action['action_name'])
                sa = ScheduleAction(schedule=s, action=a)

                if action['trigger_from'] != None:
                    ad = ActionDevice.objects.get(action=a, parameter_position=action['trigger_from'])
                    sa.trigger_device = ad
                sa.save()


class ConfigurationForm(forms.Form):
    actions = forms.CharField(required=True)

    def clean_actions(self):
        print "actions about to clean"
        data_json = self.cleaned_data['actions']
        data = simplejson.loads(data_json)

        logger.debug( 'Data extracted from request: {0}'.format( data ) )
        
        for action in data:
            # Validate action
            if not Action.objects.filter(name=action['action']).exists():
                raise forms.ValidationError('Action {0} does not exist.'
                                            .format(action['action']))
            
            # Validate devices in action
            for device in action['devices']:
                
                #device_interfaces = (Interface.objects
                #                     .filter(device__owner__username=device.split('@')[0],
                #                             device__name=device.split('@')[1]))
                #if len(device_interfaces) == 0:
                #    raise forms.ValidationError('Device {0} does not '
                #                                'implement any interfaces.'
                #                                .format(device))

                if not Device.objects.filter(owner__username=device.split('@')[0],
                                             name=device.split('@')[1]).exists():
                    raise forms.ValidationError('Device {0} does not exist.'
                                                .format(device))
            
            # Validate action roles
            num_roles = (ActionDevice.objects
                         .filter(action__name=action['action']).count())
            if len(action['roles']) != num_roles:
                raise forms.ValidationError('Action {0} has {1} roles.'
                                            .format(action['action'],
                                                    num_roles))
            
            # Check also that a device has the interfaces that a role requires
            for position, device in enumerate(action['roles']):
                if device != '_anyvalue_':
                    # If the device is in the devices list, it is a valid
                    # device
                    if device not in action['devices']:
                        raise forms.ValidationError('Device {0} is not '
                                                    'in the devices list.'
                                                    .format(device))

                    device_interfaces = (Interface.objects
                                            .filter(device__pk=device))
                    role_interfaces = (Interface.objects
                                        .filter(actiondevice__parameter_position=position,
                                               actiondevice__action__name=action['action']))
                    if len(device_interfaces) == 0:
                        raise forms.ValidationError('Device {0} does not '
                                                    'implement any interfaces.'
                                                    .format(device))

                    for interface in role_interfaces:
                        if interface not in device_interfaces:
                            raise forms.ValidationError('Device {0} has been '
                                                        'assigned to the role '
                                                        'in position {1} of action {2}, although '
                                                        'the device does not implement '
                                                        'interface {3}'
                                                        .format(device,
                                                                position + 1,
                                                                action['action'],
                                                                interface.name))
            
            # TODO: validation of parameters
            a = Action.objects.get( name=action['action'] )
            if 'parameters' in action.keys():
                for apm in a.actionpreconditionmethod_set.all():
                    action_args = set(apm.method.methodparameter_set.values_list('name', flat=True))
                    if not action_args.issubset(set(action['parameters'].keys())):
                        raise forms.ValidationError('Not enough parameters '
                                                    'supplied for configuring action {0}'
                                                    .format( action['action'] ) )
        return data_json


"""This module provides classes that generate configuration models.

New classes can be implemented for any configuration models that need
to be supported.

Exported classes:
    * :class:`KumbangModelGenerator`: A class for generating Kumbang models.

"""

from django.db.models import Count
from django.template.loader import render_to_string
from itertools import combinations
import logging
import re

logger = logging.getLogger(__name__)


class KumbangModelGenerator(object):
    """A class for generating Kumbang models.

    This class is responsible for generating a Kumbang model based on a
    schedule. The model contains all devices that have registered
    themselves.

    Instance attributes:
        * indent_with: A string of spaces that is used in the model to
          indent statements.
        * indentation: An integer count of the current indentation level in
          the model.
        * result: A list of strings representing the configuration model.

    Public functions:
        * generate_configuration_model: Generate a Kumbang configuration model.

    """

    def __init__(self):
        """Initialize the KumbangModelGenerator."""
        self.indent_with = ' ' * 4
        self.indentation = 0
        self.result = []

    def _write(self, string):
        """Append a string to the end of the configuration model.

        Args:
            * string: The string to be appended to the end of the
              configuration model.

        """
        # Add indentation, if the current indentation level is not 0.
        if self.indentation:
            self.result.append(self.indent_with * self.indentation)
        self.result.append(string)

    def _convert_mac_address(self, mac_address):
        """Convert a mac address to a format that can be used in Kumbang
        models.

        Replaces the colons in a mac address with underscores.

        Args:
            * mac_address: A mac address string, e.g., aa:bb:cc:dd:ee:ff.

        Returns:
            * A string, e.g., aa_bb_cc_dd_ee_ff.

        """
        return mac_address.replace(":", "_")

    def _append_header(self, schedule):
        """Generate the header of a Kumbang configuration model.

        An example of the generated header::

            Kumbang model schedule_calendarReminder
                root component Schedule
                root feature Status

        Args:
            * schedule: The :class:`Schedule` object for which the
              configuration model is generated.

        """
        self._write('Kumbang model schedule_%s\n' % schedule.name)
        self.indentation += 1
        self._write('root component Schedule\n')
        self._write('root feature Status\n\n\n')
        self.indentation -= 1

    def _append_attributes(self, devices):
        """Generate the attributes of a Kumbang configuration model.

        An example of the generated attributes::

            attribute type Boolean = { true, false }
            attribute type ID = { Trigger_00_00_00_00_00_01,
                                  Trigger_00_00_00_00_00_02,
                                  Trigger_00_00_00_00_00_03 }

        Args:
            * devices: A list of :class:`Device` objects that implement
              the interfaces used in the actions of the schedule.

        """
        self._write('// --- attributes ----------------------------\n\n')
        self._write('attribute type Boolean = { true, false }\n')

        device_list = []
        for device in devices:
            mac_address = self._convert_mac_address(device.mac_address)
            device_list.append('Trigger_%s' % mac_address)
        self._write('attribute type ID = { %s }\n\n\n' %
                    ', '.join(device_list))

    def _append_features(self, schedule, devices, action_methods):
        """Generate the features of a Kumbang configuration model.

        This method only generates the root feature type and calls other
        methods in order to generate the attributes, constraints and
        implementations.

        Args:
            * schedule: The :class:`Schedule` object for which the
              configuration model is generated.
            * devices: A list of :class:`Device` objects that implement
              the interfaces used in the actions of the schedule.
            * action_methods: A list of :class:`Method` objects used in
              the actions of the schedule.

        """
        self._write('// --- features ------------------------------\n\n')
        self._write('feature type Status {\n')
        self.indentation += 1

        self._append_feature_attributes(devices, action_methods)
        self.indentation -= 1
        self._append_feature_constraints(devices)
        self.indentation -= 1
        self._append_feature_implementations(schedule, devices, action_methods)

        self.indentation -= 2
        self._write('}\n\n\n')

    def _append_feature_attributes(self, devices, action_methods):
        """Generate the feature attributes of a Kumbang configuration model.

        An example of the generated feature attributes::

            attributes
                // triggering device
                ID trigger;
                // device ff_ff_ff_ff_ff_ff
                Boolean eventApproaching_ff_ff_ff_ff_ff_ff;
                Boolean isInProximity_ff_ff_ff_ff_ff_ff;
                // device ee_ee_ee_ee_ee_ee
                Boolean eventApproaching_ee_ee_ee_ee_ee_ee;
                Boolean isInProximity_ee_ee_ee_ee_ee_ee;
                // device 00_00_00_00_00_01
                Boolean isInProximity_00_00_00_00_00_01;

        Args:
            * devices: A list of :class:`Device` objects that implement
              the interfaces used in the actions of the schedule.
            * action_methods: A list of :class:`Method` objects used in
              the actions of the schedule.

        """
        self._write('attributes\n')
        self.indentation += 1
        self._write('// triggering device\n')
        self._write('ID trigger;\n')

        for device in devices:
            mac_address = self._convert_mac_address(device.mac_address)
            self._write('// device %s\n' % mac_address)

            for method in action_methods:
                if device.interfaces.filter(pk=method.interface.id).exists():
                    self._write('Boolean %s_%s;\n' % (method.name,
                                                      mac_address))

            self._write('Boolean isInProximity_%s;\n' % mac_address)

    def _append_feature_constraints(self, devices):
        """Generate the feature constraints of a Kumbang configuration model.

        An example of the generated feature constraints::

            constraints
                // proximities
                value(isInProximity_ff_ff_ff_ff_ff_ff) = false =>
                    not has_instances(Device_ff_ff_ff_ff_ff_ff);
                value(isInProximity_ee_ee_ee_ee_ee_ee) = false =>
                    not has_instances(Device_ee_ee_ee_ee_ee_ee);
                value(isInProximity_00_00_00_00_00_01) = false =>
                    not has_instances(Device_00_00_00_00_00_01);
                value(isInProximity_00_00_00_00_00_06) = false =>
                    not has_instances(Device_00_00_00_00_00_06);

        Args:
            * devices: A list of :class:`Device` objects that implement
              the interfaces used in the actions of the schedule.

        """
        self._write('constraints\n')
        self.indentation += 1
        self._write('// proximities\n')

        for device in devices:
            mac_address = self._convert_mac_address(device.mac_address)
            self._write('value(isInProximity_%s) = false => '
                        'not has_instances(Device_%s);\n' %
                        (mac_address, mac_address))

    def _append_feature_implementations(self, schedule,
                                        devices, action_methods):
        """Generate the feature implementations of a Kumbang configuration
        model.

        An example of the generated feature implementations::

            implementation
                // status eventApproaching
                not (value(eventApproaching_ff_ff_ff_ff_ff_ff) = true) =>
                    not instance_of(component-root.action.trigger,
                                    Device_ff_ff_ff_ff_ff_ff);
                not (value(eventApproaching_ee_ee_ee_ee_ee_ee) = true) =>
                    not instance_of(component-root.action.trigger,
                                    Device_ee_ee_ee_ee_ee_ee);
                // trigger
                value(trigger) = Trigger_ff_ff_ff_ff_ff_ff =>
                    instance_of(component-root.action.trigger,
                                Device_ff_ff_ff_ff_ff_ff) and
                    not instance_of(component-root.action.devices,
                                    Device_ff_ff_ff_ff_ff_ff);
                value(trigger) = Trigger_ee_ee_ee_ee_ee_ee =>
                    instance_of(component-root.action.trigger,
                                Device_ee_ee_ee_ee_ee_ee) and
                    not instance_of(component-root.action.devices,
                                    Device_ee_ee_ee_ee_ee_ee);

        Args:
            * schedule: The :class:`Schedule` object for which the
              configuration model is generated.
            * devices: A list of :class:`Device` objects that implement
              the interfaces used in the actions of the schedule.
            * action_methods: A list of :class:`Method` objects used in
              the actions of the schedule.

        """
        self._write('implementation\n')
        self.indentation += 1

        trigger_methods = []
        devices_methods = []

        # Get the action devices that are the triggers for the actions
        trigger_devices = []
        schedule_actions = (models.ScheduleAction
                                  .objects
                                  .filter(schedule=schedule))
        for schedule_action in schedule_actions:
            trigger_devices.append(schedule_action.trigger_device)

        # Get all actions of the schedule
        actions = schedule.actions.all()
        for action in actions:
            # Get all action devices that are listed in the action precondition
            # as parameters
            action_devices = action.actiondevice_set.all()
            for action_device in action_devices:
                if action_device in trigger_devices:
                    precondition_methods = (action_device
                                            .actionpreconditionmethod_set
                                            .exclude(method__in=trigger_methods))
                    for precondition_method in precondition_methods:
                        trigger_methods.append(precondition_method.method)
                else:
                    precondition_methods = (action_device
                                            .actionpreconditionmethod_set
                                            .exclude(method__in=devices_methods))
                    for precondition_method in precondition_methods:
                        devices_methods.append(precondition_method.method)

        for method in action_methods:
            self._write('// status %s\n' % method.name)

            for device in devices:
                if device.interfaces.filter(pk=method.interface.id).exists():
                    mac_address = self._convert_mac_address(device.mac_address)
                    consequents = []
                    if method in devices_methods:
                        consequents.append('not instance_of('
                                           'component-root.action.devices, '
                                           'Device_%s)' % mac_address)
                    if method in trigger_methods:
                        consequents.append('not instance_of('
                                           'component-root.action.trigger, '
                                           'Device_%s)' % mac_address)

                    self._write('not (value(%s_%s) = true) => %s;\n' %
                                (method.name, mac_address,
                                 ' and '.join(consequents)))

        self._write('// trigger\n')
        for device in devices:
            mac_address = self._convert_mac_address(device.mac_address)
            self._write('value(trigger) = Trigger_%(mac_address)s => '
                        'instance_of(component-root.action.trigger, '
                        'Device_%(mac_address)s) and '
                        'not instance_of(component-root.action.devices, '
                        'Device_%(mac_address)s);\n' %
                        {'mac_address': mac_address})

    def _append_components(self, schedule, devices, actions, interfaces):
        """Generate the components of a Kumbang configuration model.

        Args:
            * schedule: The :class:`Schedule` object for which the
              configuration model is generated.
            * devices: A list of :class:`Device` objects that implement
              the interfaces used in the actions of the schedule.
            * actions: A list of :class:`Action` objects that are declared
              in the schedule.
            * interfaces: A list of :class:`Interface` objects used in
              the actions of the schedule.

        """
        self._write('// --- components ----------------------------\n\n')
        self._append_component_root(actions)
        self._append_component_actions(schedule, actions)
        self._append_component_interfaces(interfaces)
        self._append_component_devices(devices, interfaces)

    def _append_component_root(self, actions):
        """Generate the root component of a Kumbang configuration model.

        In this case, the root component is the Schedule component. For
        example::

            component type Schedule {
                contains
                    (FakeCall, Conversation) action;
            }

        Args:
            * actions: A list of :class:`Action` objects that are declared
              in the schedule.

        """
        self._write('component type Schedule {\n')
        self.indentation += 1
        self._write('contains\n')
        self.indentation += 1

        action_names = []
        for action in actions:
            action_names.append('%s' % action.name)

        self._write('(%s) action;\n' % ', '.join(action_names))
        self.indentation -= 2
        self._write('}\n\n')

    def _append_component_actions(self, schedule, actions):
        """Generate the subcomponents of a Kumbang configuration model.

        In this case, the subcomponents are the actions of a schedule. For
        example::

            component type FakeCall {
                contains
                    TalkingDevice devices;
                    CalendarSource trigger;
                constraints
                    instance_of(trigger, TalkingDevice);
            }

        Args:
            * schedule: The :class:`Schedule` object for which the
              configuration model is generated.
            * actions: A list of :class:`Action` objects that are declared
              in the schedule.

        """
        for action in actions:
            self._write('component type %s {\n' % action.name)
            self.indentation += 1
            self._write('contains\n')
            self.indentation += 1

            # try else
            schedule_action = (models.ScheduleAction
                                     .objects
                                     .get(schedule=schedule, action=action))

            action_devices = (action.actiondevice_set
                                    .all()
                                    .order_by('parameter_position'))
            component_action_devices = {}
            for action_device in action_devices:
                action_device_interfaces = (action_device.interfaces
                                                         .all()
                                                         .order_by('name'))
                component_interface_list = []
                component_interface_name = ''
                for action_device_interface in action_device_interfaces:
                    component_interface_list.append(action_device_interface
                                                    .name)
                    component_interface_name += action_device_interface.name

                component_name = ''
                # If the action device is the trigger
                if (schedule_action.trigger_device.parameter_position ==
                    action_device.parameter_position):
                    component_name = 'trigger'
                else:
                    component_name = 'devices'

                if component_interface_name not in component_action_devices:
                    component_action_devices[component_interface_name] = {
                            'component_name': component_name,
                            'num_devices': 1,
                            'interfaces': component_interface_list}
                else:
                    component_action_devices[component_interface_name]['num_devices'] += 1

            multiple_interfaces = False
            for component_action_device in component_action_devices.values():
                interface_name = component_action_device['interfaces'].pop(0)
                if len(component_action_device['interfaces']):
                    multiple_interfaces = True

                if component_action_device['num_devices'] == 1:
                    self._write('%s %s;\n' %
                                (interface_name,
                                 component_action_device['component_name']))
                else:
                    self._write('%s %s[%i] { different };\n' %
                                (interface_name,
                                 component_action_device['component_name'],
                                 component_action_device['num_devices']))

            if multiple_interfaces:
                self.indentation -= 1
                self._write('constraints\n')
                self.indentation += 1
                for component_action_device in component_action_devices.values():
                    for interface_name in component_action_device['interfaces']:
                        self._write('instance_of(%s, %s);\n' %
                                    (component_action_device['component_name'],
                                     interface_name))

            self.indentation -= 2
            self._write('}\n\n')

    def _append_component_interfaces(self, interface_lists):
        """Generate the components for the interfaces.

        An example of the generated interface components::

            abstract component type CalendarSource {}
            abstract component type TalkingDevice {}

        Args:
            * interfaces: A list of :class:`Interface` objects used in
              the actions of the schedule.

        """
        defined_interfaces = []
        for interface_list in interface_lists:
            for interface in interface_list:
                if interface.name not in defined_interfaces:
                    self._write('abstract component type %s {}\n' %
                                interface.name)
                    defined_interfaces.append(interface.name)
        self._write('\n')

    def _append_component_devices(self, devices, interface_lists):
        """Generate the components for the devices.

        An example of the generated device components::

            component type Device_ff_ff_ff_ff_ff_ff extends
                (CalendarSource, TalkingDevice) {}
            component type Device_ee_ee_ee_ee_ee_ee extends
                (CalendarSource, TalkingDevice) {}
            component type Device_00_00_00_00_00_01 extends TalkingDevice {}
            component type Device_00_00_00_00_00_06 extends TalkingDevice {}

        Args:
            * devices: A list of :class:`Device` objects that implement
              the interfaces used in the actions of the schedule.
            * interface_lists: A list of :class:`Interface` objects used in
              the actions of the schedule.

        """
        for device in devices:
            mac_address = self._convert_mac_address(device.mac_address)

            device_interfaces = []
            for interface_list in interface_lists:
                for interface in interface_list:
                    if (interface.name not in device_interfaces and
                        device.interfaces.filter(pk=interface.id).exists()):
                        device_interfaces.append(interface.name)
            device_interface_name = ', '.join(device_interfaces)
            if len(device_interfaces) > 1:
                device_interface_name = '(%s)' % device_interface_name
            self._write('component type Device_%s extends %s {}\n' %
                        (mac_address, device_interface_name))

    def generate_configuration_model(self, schedule):
        """Generate a Kumbang configuration model.

        The Kumbang configuration model is generated based on the schedule
        given as argument. The configuration model contains all devices
        that implement interfaces present in the actions of the schedule.

        Args:
            * schedule: The :class:`Schedule` object for which the
              configuration model is generated.

        Returns:
            * A Kumbang model as a string encoded in UTF-8.

        """
        interfaces = []
        action_methods = []
        action_method_ids = []

        # Get all actions of the schedule
        actions = schedule.actions.all()
        for action in actions:
            # Get all action devices that are listed in the action precondition
            # as parameters
            action_devices = action.actiondevice_set.all()
            for action_device in action_devices:
                # Get all the interfaces of the devices in the action
                # precondition parameters
                action_device_interfaces = list(action_device.interfaces
                                                             .all()
                                                             .order_by('name'))

                # Append the list of interfaces to a list of interface lists
                if not action_device_interfaces in interfaces:
                    interfaces.append(action_device_interfaces)
#                # Get all the interfaces of the devices in the action
#                # precondition parameters
#                # that are not already in the interfaces list
#                action_device_interfaces = (action_device.interfaces.
#                                            exclude(name__in=interfaces.keys()))
#                for action_device_interface in action_device_interfaces:
#                    interface_name = action_device_interface.name
#                    interfaces[interface_name] = action_device_interface

            # Get all precondition methods that are used in the actions
            precondition_methods = (action.actionpreconditionmethod_set
                                          .exclude(method__id__in=action_method_ids))
            for precondition_method in precondition_methods:
                if not precondition_method.method.id in action_method_ids:
                    action_method_ids.append(precondition_method.method.id)
                    action_methods.append(precondition_method.method)
            # Get all precondition methods that are used in the actions
#            precondition_methods = (action.actionpreconditionmethod_set.
#                                    exclude(method__id__in=action_methods.keys()))
#            for precondition_method in precondition_methods:
#                if precondition_method.method.id not in action_methods:
#                    method_id = precondition_method.method.id
#                    action_methods[method_id] = precondition_method.method

        device_ids = []
        devices = []
        for interface_list in interfaces:
            # TODO the devices could be given as a parameter to the method
            devices_tmp = (models.Device
                                 .objects
                                 .filter(interfaces__in=interface_list)
                                 .annotate(num_interfaces=Count('id'))
                                 .filter(num_interfaces=len(interface_list))
                                 .exclude(id__in=device_ids))
            device_ids += devices_tmp.values_list('id', flat=True)
            devices += list(devices_tmp)

        self._append_header(schedule)
        self._append_attributes(devices)
        self._append_features(schedule, devices, action_methods)
        self._append_components(schedule, devices, actions, interfaces)

        #devices.append({'devices': list(devices_tmp),
        #                'interfaces': interface_list})
        # Fetch all devices that implement all the interfaces in the actions of
        # the schedule
        # Note that this does not count distinct values
        #devices = (models.Device.objects.
        #           filter(interfaces__name__in=interfaces.keys()).
        #           annotate(num_interfaces=Count('id')).
        #           filter(num_interfaces=len(interfaces)))

        kumbang_model = ''.join(self.result).encode('UTF-8')
        
        return kumbang_model


class WcrlModelGenerator(object):
    
    def _convert_mac_address(self, mac_address):
        """Convert a mac address to a format that can be used in Wcrl
        models.

        Replaces the colons in a mac address with underscores.

        Args:
            * mac_address: A mac address string, e.g., aa:bb:cc:dd:ee:ff.

        Returns:
            * A string, e.g., aa_bb_cc_dd_ee_ff.

        """
        return mac_address.replace(":", "_")    
    
    def get_dev_pk(self, device_id):
        """Returns unique device key if identifier can be matched.
        
        Note: for lookups device_id can contain other identifying info as well.
        
        Args:
            * device_id: device identification info
        
        Returns:
            * matched device primary key (integer) if unique match cannot be made, returns None
    
        """
        #logger.debug( 'Identifying a device based on description: {0}'.format(device_id) )
        reg_mac = r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2})'   
        
        if re.search(reg_mac, device_id) != None:
            return models.Device.objects.get(mac_address=device_id).pk
        elif '@' in device_id:
            return models.Device.objects.get(owner__username=device_id.split('@')[0],
                                             name=device_id.split('@')[1]).pk
        else:
            try:
                i = int(device_id)
                return i
            except ValueError:
                logger.error( 'No device could be matched for device_id: {0}'.format(device_id) )
        
        return None
    
    
    def _get_model_input(self, configurable_actions):
        model_input = {'actions': [], 'devices':[]}

        # bit of a hack to enable support for action-wise configuration
        if type(configurable_actions) != type(list()):
            configurable_actions = [configurable_actions]
        

        for configurable_action in configurable_actions:
            action_dict = {'name': '', 'roles': []}

            try:
                action = (models.Action
                          .objects
                          .get(name=configurable_action['action']))
            except models.Action.DoesNotExist:
                logger.debug('Action {0} does not exist.'
                             .format(configurable_action['action']))
                return None
            else:
                action_dict['name'] = action.name

                action_roles = (action.actiondevice_set
                                .all()
                                .order_by('parameter_position'))
                for role in action_roles:
                    role_dict = {'name': '', 'interfaces': [],
                                 'preconditions': []}
                    role_dict['name'] = role.name
                    # Get a list of interface names that the role requires
                    role_dict['interfaces'] = (role.interfaces
                                               .values_list('name', flat=True))

                    preconditions = (role.actionpreconditionmethod_set.all()
                                     .order_by('expression_position'))
                    for precondition in preconditions:
                        precondition_dict = {'interface': '', 'method': '',
                                             'value': ''}
                        precondition_dict['interface'] = (precondition.method
                                                          .interface.name)
                        precondition_dict['method'] = (precondition.method
                                                       .name)
                        # TODO: this has to be done better, change the database
                        # structure to allow a value in the precondition table
                        precondition_dict['value'] = 'true'

                        role_dict['preconditions'].append(precondition_dict)

                    action_dict['roles'].append(role_dict)

                # add device singularity constraints
                action_dict['constr'] = list( combinations( [i['name'] for i in action_dict['roles']], 2 ) )

                model_input['actions'].append(action_dict)
        
        
    
        # append devices and interfaces
        for caction in configurable_actions:
            for device_id in caction['devices']:
                if filter( lambda x: device_id in x.values(), model_input['devices'] ):
                    continue
                else:
                    device_dict = {}
                    device_dict['id'] = device_id
                    device_dict['interfaces'] = models.Device.objects.get(pk=device_id).interfaces.values_list('name', flat=True)
                    model_input['devices'].append( device_dict )
    
        #logger.debug('model ctx generation, model_input: {0}'.format( model_input ))

        
        return model_input

    def _get_selection_input(self, configurable_actions):
        selection_input = {'devices': []}
        
        # bit of a hack to enable support for action-wise configuration
        if type(configurable_actions) != type(list()):
            configurable_actions = [configurable_actions]
        
        for configurable_action in configurable_actions:
            # check for extra parameters, that may or may not affect the state value
            check_params = False
            if 'parameters' in configurable_action.keys():
                check_params = True

            # The devices in the action configuration that have not been
            # assigned to any roles
            unassigned_devices = []
            for device_id in configurable_action['devices']:
                if device_id not in configurable_action['roles']:
                    unassigned_devices.append(device_id)
            #logger.debug('Unassigned devices: {0}'.format(unassigned_devices))
            try:
                action = (models.Action
                          .objects
                          .get(name=configurable_action['action']))
            except models.Action.DoesNotExist:
                logger.debug('Action {0} does not exist.'
                             .format(configurable_action['action']))
                return None
            else:
                action_roles = (action.actiondevice_set
                                .all()
                                .order_by('parameter_position'))
                for role in action_roles:
                    role_interfaces = (role.interfaces
                                       .values_list('name', flat=True))
                            
                    if not role_interfaces or not role.actionpreconditionmethod_set.exists():
                        continue
                    
                    logger.debug( 'role_interfaces: {0}'.format(role_interfaces) )

                    if configurable_action['roles'][role.parameter_position] != '_anyvalue_':
                        device_dict = {'role':'role_'+configurable_action['action']+'_'+role.name}
                        device_dict['id'] = configurable_action['roles'][role.parameter_position]
                        
                        logger.debug( 'setting pre-matched role {0} for role: {1}'.format( device_dict['role'], role.name ) )
                        #device_dict['interfaces'] = role.interfaces.values_list('name',flat=True)
                        #device = models.Device.objects.get(pk=device_dict['id'])
                        #state_struct = list(device.statevalue_set
                        #                    .filter(method__interface__name__in=device_dict['interfaces'])
                        #                    .values_list('method__name', 'value'))
                        #device_dict['stateValues'] = map( lambda i: dict(zip(('method','value'),i)),state_struct )
                        selection_input['devices'].append(device_dict)
                    else:
                        for device_id in unassigned_devices:
                            #logger.debug( 'dev_id in unassigned devs: {0}'.format(device_id) )
                            
                            device_dict = {'id': '', 'interfaces': [], 'stateValues': []}
                            update_only = False
                            
                            state_struct = []
                            #already a candidate for different role?
                            for item in selection_input['devices']:
                                if device_id in item.values():
                                    device_dict = item
                                    update_only = True

                            role_preconditions = role.actionpreconditionmethod_set.all()
                            device = models.Device.objects.get(pk=device_id)
                            
                            for apm in role_preconditions:
                                try:
                                    statevalue = device.statevalue_set.get(method__name=apm.method.name,
                                                                           method__interface__name=apm.method.interface.name)
                                    
                                    sv_args = statevalue.statevalueargument_set.values_list('method_parameter__name', 'value')
                                    
                                    if sv_args:
                                        if set(sv_args).issubset(set(configurable_action['parameters'].items())):
                                            state_struct.append( dict([('method',apm.method.name),('value',statevalue.value)]) )
                                        else:
                                            state_struct.append( dict([('method',apm.method.name),('value','false')]) )
                                    else:
                                        state_struct.append( dict([('method',apm.method.name),('value',statevalue.value)]) )
                                except Exception: 
                                    continue
                            
                            
                            device_dict['stateValues'] += state_struct
                            
                            #remove duplicates
                            device_dict['stateValues'] = [dict(t) for t in set([tuple(d.items()) for d in device_dict['stateValues']])]

                            device_dict['interfaces'] += role_interfaces
                            device_dict['interfaces'] = list( set(device_dict['interfaces']) )
                            
                            device_dict['id'] = device_id

                            if not update_only:
                                selection_input['devices'].append(device_dict)
        
        #logger.debug( 'Selection input: {0}'.format( selection_input ) )
                
        return selection_input


    def generate_configuration_model(self, configurable_actions):
        ctx_dict = self._get_model_input(configurable_actions)
        wcrl_model = render_to_string('model_templates/wcrl_model.lp',
                                      ctx_dict)

        # Fix the indentation caused by django's templates
        wcrl_model = re.sub(r'^[^\S\n]+', '', wcrl_model, flags=re.MULTILINE)
        wcrl_model = re.sub(r'\n{2}', '\n', wcrl_model, flags=re.MULTILINE)
        wcrl_model = re.sub(r'^\n{2,}', '\n', wcrl_model, flags=re.MULTILINE)
        
        return wcrl_model

    def generate_configuration_selections(self, configurable_actions):

        ctx_dict = self._get_selection_input(configurable_actions)
        configuration_selections = render_to_string('model_templates/wcrl_selections.lp',
                                                    ctx_dict)

        # Fix the indentation caused by django's templates
        configuration_selections = re.sub(r'^[^\S\n]+', '', configuration_selections, flags=re.MULTILINE)
        configuration_selections = re.sub(r'\n{2}', '\n', configuration_selections, flags=re.MULTILINE)
        configuration_selections = re.sub(r'^\n{2,}', '\n', configuration_selections, flags=re.MULTILINE)

        return configuration_selections

# This has been put here to break a circular import
import models

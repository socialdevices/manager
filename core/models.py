"""This module provides model classes used by Django.

The model classes define the database structure and should contain
all business logic that manipulate the data.

Exported classes:
    * :class:`Base`: An abstract base class that can be inherited by other
      model classes.
    * :class:`Interface`: A model class for social device interfaces.
    * :class:`Device`: A model class for social devices.
    * :class:`DeviceInterface`: A model class for device and interface
      relationships.
    * :class:`DataType`: A model class for data types (not used).
    * :class:`Method`: A model class for interface methods.
    * :class:`MethodParameter`: A model class for method parameters.
    * :class:`StateValue`: A model class for state (method) values.
    * :class:`StateValueArgument`: A model class for state value arguments.
    * :class:`Action`: A model class for actions.
    * :class:`Trigger`: A model class for triggers.
    * :class:`Schedule`: A model class for schedules.
    * :class:`ActionDevice`: A model class for the devices that are defined
      in actions.
    * :class:`ScheduleAction`: A model class for schedule and action
      relationships.
    * :class:`ActionDeviceInterface`: A model class for the relationship
      between action devices and interfaces.
    * :class:`ActionPreconditionMethod`: A model class for precondition methods
      defined in actions.

"""

from core import signals
from core.clients import ProximityClient, ProximityClientConnectionError
from django.db import models, transaction
from django.db.models.signals import post_delete
from events.event import EventHandler
from django.contrib.auth.models import User
import logging


logger = logging.getLogger(__name__)
event_handler = EventHandler()

signals.state_triggered.connect(signals.start_configuration)
signals.schedule_added.connect(signals.generate_configuration_model)
signals.device_interface_added.connect(signals.update_configuration_models)
#signals.device_interface_deleted.connect(signals.update_configuration_models)


class Base(models.Model):
    """An abstract base class that can be inherited by other model classes.

    This class can be used for defining database fields that are common to
    many different tables.

    Class attributes:
        * created_at: A Django :class:`~django.db.models.DateTimeField` object
          for storing the date and time of creation.
        * updated_at A Django :class:`DateTimeField
          <django.db.models.DateTimeField>` object for storing the date and
          time of modification.

    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class Interface(Base):
    """A Django model class for interfaces.

    Class attributes:
        * name: A Django :class:`CharField
          <django.db.models.CharField>` object for storing the name of the
          interface.
        * interface_file: A Django :class:`FileField
          <django.db.models.FileField>` object for storing the actual interface
          file, where the interface is defined in.

    """
    name = models.CharField(max_length=255, unique=True)
    interface_file = models.FileField(upload_to='interfaces', max_length=100,
                                      null=True, blank=True)

    def __unicode__(self):
        """Return a string representation of the :class:`Interface` object."""
        return self.name

    def save(self, *args, **kwargs):
        """Save the :class:`Interface` object."""

        is_new = False
        if not self.id:
            is_new = True
        else:
            try:
                # The following lines should be in a transaction, so that an
                # interface object is not updated with an interface file
                # between the check and the delete
                with transaction.commit_on_success():
                    interface = Interface.objects.get(id=self.id)

                    # If the interface file has changed and no other Interface
                    # object references the old file, then delete the old one,
                    # because Django does not overwrite the old file and leaves
                    # it orphaned on the file system
                    if (interface.interface_file != self.interface_file and
                        not (Interface.objects
                                      .filter(interface_file=interface.interface_file)
                                      .exclude(id=self.id).exists())):
                        interface.interface_file.delete()
            except:
                pass

        super(Interface, self).save(*args, **kwargs)

        if is_new:
            event_handler.add_event(u'Interface %s added' % self.name)

# Connect a post delete signal with the deletion of interface files
post_delete.connect(signals.delete_files, sender=Interface)


class Device(Base):
    """A Django model class for devices.

    Class attributes:
        * mac_address: A Django :class:`CharField
          <django.db.models.CharField>` object for storing the mac address of
          the device.
        * name: A Django :class:`CharField
          <django.db.models.CharField>` object for storing a human-readable
          name of the device.
        * is_reserved: A Django :class:`BooleanField
          <django.db.models.BooleanField>` object for storing, if the device
          is reserved or not.
        * interfaces: A Django :class:`ManyToManyField
          <django.db.models.ManyToManyField>` object for storing a many-to-many
          relationship to :class:`Interface` objects.
        * Admin 
          who register the device, usually same as owner. Otherwise only if owner NULL 
        * Owner usually same as admin, can be NULL if stationary device
    """
    # TODO Change this field to a better data type
    mac_address = models.CharField(max_length=17,
                                   unique=True,
                                   help_text='A unique bluetooth mac address '
                                             'with a colon as the separator, '
                                             'e.g., aa:aa:aa:aa:aa:aa')
    
    name = models.CharField(max_length=255,
                            help_text='A human-readable device name')
    is_reserved = models.BooleanField(default=False,
                                      help_text='A boolean value indicating '
                                                'whether the device is '
                                                'reserved, e.g., because it '
                                                'is executing an action')
    interfaces = models.ManyToManyField(Interface, through='DeviceInterface')
    
    admin = models.ForeignKey(User, related_name='admin_device_set', null=True )
    owner = models.ForeignKey(User, related_name='owner_device_set',null=True)
    
    TYPE_CHOICES = (
        ('PR','Primary Device'),              
        ('ST','Stationary Device'),
        ('NO','None'),
    )
    
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='NO')                
                
    def __unicode__(self):
        """Return a string representation of the :class:`Device` object."""
        return self.mac_address

    def _get_id_string(self):
        if self.owner:
            return u'{0}@{1}'.format(self.owner.username,self.name)
        else:
            return u'public@{0}'.format(self.name)

    id_string = property(_get_id_string)

    def register_proximity_device(self):
        """Register the device itself to the proximity server."""
        client = ProximityClient()
        try:
            client.add_device(self.mac_address)
        except ProximityClientConnectionError, e:
            logger.error(e)
            event_handler.add_event(e)

    def set_proximity_devices(self, neighbours):
        """Set the proximity devices of the device.

        This method sets the proximity devices, i.e., the neighbouring
        devices as it's proximity devices.

        Args:
            * neighbours: A list of mac_addresses as strings, e.g.,
              ['aa:aa:aa:aa:aa:aa', 'bb:bb:bb:bb:bb:bb']

        """
        client = ProximityClient()
        try:
            client.set_group(self.mac_address, neighbours)
        except ProximityClientConnectionError, e:
            logger.error(e)
            event_handler.add_event(e)
        else:
            true_neighbour_devices = (Device.objects
                                            .filter(mac_address__in=neighbours))
            true_neighbours = []
            for device in true_neighbour_devices:
                neighbours.remove(device.mac_address)
                true_neighbours.append(device.mac_address)

            event_handler.add_event(u'%s updated its proximity devices: %r - %r' %
                                    (self.mac_address,
                                     true_neighbours,
                                     neighbours))

    def get_proximity_mac_addresses(self):
        """Get the mac addresses of the proximity devices.

        Returns:
            * A list of mac_addresses as strings, e.g.,
              ['aa:aa:aa:aa:aa:aa', 'bb:bb:bb:bb:bb:bb']
            * None, if the connection to the proximity server failed.

        """
        client = ProximityClient()
        try:
            mac_addresses = client.get_group(self.mac_address)
        except ProximityClientConnectionError, e:
            logger.error(e)
            event_handler.add_event(e)
            return None
        else:
            return mac_addresses

    def get_proximity_devices(self):
        """Get the proximity devices.

        Returns:
            * A Django :class:`QuerySet
              <django.db.models.query.QuerySet>` object containing the
              proximity devices as :class:`Device` objects.

        """
        mac_addresses = self.get_proximity_mac_addresses()

        devices = Device.objects.filter(mac_address__in=mac_addresses)

        return devices

    proximity_device_group = property(get_proximity_devices,
                                      set_proximity_devices)

    def _get_num_proximity_devices(self):
        """Get the number of proximity devices of the device.

        Returns:
            * The number of proximity devices as an integer.
            * -1, if the number of proximity devices is not available.

        """
        mac_addresses = self.get_proximity_mac_addresses()

        if mac_addresses != None:
            return len(mac_addresses)
        else:
            return -1

    num_proximity_devices = property(_get_num_proximity_devices)

    def save(self, *args, **kwargs):
        """Save the :class:`Device` object."""
        is_new = False
        if not self.id:
            is_new = True
        elif Device.objects.get(id=self.id).is_reserved != self.is_reserved:
            event_handler.add_event('Device %s set %s' %
                                    (self.mac_address,
                                     ('Available', 'Reserved')[self.is_reserved]))

        super(Device, self).save(*args, **kwargs)

        if is_new:
            self.register_proximity_device()
            event_handler.add_event(u'%s registered to Kurre' %
                                    self.mac_address)


class DeviceInterface(models.Model):
    """A Django model class for device-interface relationships.

    Class attributes:
        * device: A Django :class:`ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship
          to a :class:`Device` object.
        * interface: A Django :class:`ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          an :class:`Interface` object.
        * created_at: A Django :class:`DateTimeField
          <django.db.models.DateTimeField>` object for storing the date and
          time, when the relationship was created.

    """
    device = models.ForeignKey(Device)
    interface = models.ForeignKey(Interface)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = ("device", "interface")

    def __unicode__(self):
        """Return a string representation of the :class:`DeviceInterface`
        object."""
        return u'%s - %s' % (self.device.mac_address, self.interface.name)

    def save(self, *args, **kwargs):
        """Save the :class:`DeviceInterface` object."""
        is_new = False
        if not self.id:
            is_new = True

        super(DeviceInterface, self).save(*args, **kwargs)

        if is_new:
            event_handler.add_event(u'%s implements interface %s' %
                                    (self.device.mac_address,
                                     self.interface.name))

            # Send signal
            signals.device_interface_added.send(sender=self,
                                                device=self.device,
                                                interface=self.interface)

# Connect a post delete signal of DeviceInterface with the update of the
# configuration models
post_delete.connect(signals.update_configuration_models,
                    sender=DeviceInterface)


class DataType(Base):
    """A Django model class for data types.

    Currently, this class is not used anywhere.

    Class attributes:
        * name: A Django :class:`CharField
          <django.db.models.CharField>` object for storing the name of the data
          type.

    """
    name = models.CharField(max_length=30, unique=True)

    def __unicode__(self):
        """Return a string representation of the :class:`DataType` object."""
        return self.name


class Method(Base):
    """A Django model class for interface methods.

    Class attributes:
        * name: A Django :class:`CharField
          <django.db.models.CharField>` object for storing the name of the
          method.
        * interface: A Django :class:`ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          an :class:`Interface` object.
        * return_data_type: A Django :class:`ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          a :class:`DataType` object. In practice, this is not used anywhere.

    """
    name = models.CharField(max_length=255)
    interface = models.ForeignKey(Interface)
    return_data_type = models.ForeignKey(DataType,
                                         blank=True,
                                         null=True,
                                         on_delete=models.SET_NULL)

    class Meta:
        unique_together = ("name", "interface")

    def __unicode__(self):
        """Return a string representation of the :class:`Method` object."""
        return u'%s - %s' % (self.interface.name, self.name)

    def save(self, *args, **kwargs):
        """Save the :class:`Method` object."""
        is_new = False
        if not self.id:
            is_new = True

        super(Method, self).save(*args, **kwargs)

        if is_new:
            event_handler.add_event(u'Method %s added for interface %s' %
                                    (self.name, self.interface.name))


class MethodParameter(Base):
    """A Django model class for method parameters.

    Class attributes:
        * name: A Django :class:`CharField
          <django.db.models.CharField>` object for storing the name of the
          method parameter.
        * method: A Django :class:`ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          a :class:`Method` object.
        * data_type: A Django :class:`ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          a :class:`DataType` object. In practice, this is not used anywhere.

    Instance attributes:
        * arguments: A dictionary of method parameters and their corresponding
          values.

    """
    name = models.CharField(max_length=30)
    method = models.ForeignKey(Method)
    data_type = models.ForeignKey(DataType,
                                  blank=True,
                                  null=True,
                                  on_delete=models.SET_NULL)

    class Meta:
        unique_together = ("name", "method")

    def __unicode__(self):
        """Return a string representation of the :class:`MethodParameter`
        object."""
        return u'%s - %s' % (self.method.name, self.name)


class StateValue(Base):
    """A Django model class for state values (method values).

    Class attributes:
        * value: A Django :class:`CharField
          <django.db.models.CharField>` object for storing the value of the
          method.
        * device: A Django :class:`ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          a :class:`Device` object.
        * method: A Django :class:`ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          a :class:`Method` object.

    """
    value = models.CharField(max_length=255)
    device = models.ForeignKey(Device)
    method = models.ForeignKey(Method)

    class Meta:
        unique_together = ("device", "method")

    def __init__(self, *args, **kwargs):
        """Initialize the StateValue object.

        The init method is overridden, because an instance attribute is
        declared. The instance attribute is used to store the state value
        arguments in resources_v2.py. This is done, so that the state value
        arguments can be added to the database after the state value has been
        saved and before the trigger is executed. This ensures that the state
        value arguments are actually in the database before the configuration
        is started.

        """
        super(Base, self).__init__(*args, **kwargs)
        self.arguments = {}

    def __unicode__(self):
        """Return a string representation of the :class:`StateValue`
        object."""
        return u'%s - %s - %s = %s' % (self.device.mac_address,
                                       self.method.interface.name,
                                       self.method.name,
                                       self.value)

    def _is_triggering(self):
        """Check whether the method for which a value is stored is a trigger.

        Returns:
            * A Django :class:`QuerySet
              <django.db.models.query.QuerySet>` object containing all
              :class:`Schedule` objects that the method is a trigger for,
              if the method is a trigger.
            * False, if the method is not a trigger.

        """
        try:
            schedules = (Trigger.objects
                                .get(method=self.method)
                                .schedule_set
                                .all())
        except Trigger.DoesNotExist:
            schedules = False

        return schedules

    def save(self, *args, **kwargs):
        """Save the :class:`StateValue` object."""
        is_new = False
        if not self.id:
            is_new = True

        super(StateValue, self).save(*args, **kwargs)

        argument_list = []
        # Add the state value arguments to the database
        # This is done here, so that the state value and the arguments will be
        # saved at the same time. Otherwise, when a trigger is updated, the
        # arguments might not be available, if they are saved after the state
        # value.
        for name, value in self.arguments.items():
            try:
                mp = MethodParameter.objects.get(name=name)
            except MethodParameter.DoesNotExist:
                logger.error('Method parameter %s does not exist for method %s' %
                             (name, self.method.name))
            else:
                if is_new:
                    self.statevalueargument_set.create(method_parameter=mp,
                                                       value=value)
                else:
                    try:
                        sva = self.statevalueargument_set.get(method_parameter=mp)
                    except StateValueArgument.DoesNotExist:
                        self.statevalueargument_set.create(method_parameter=mp,
                                                           value=value)
                    else:
                        sva.value = value
                        sva.save()
                argument_list.append('%s=%s' % (name, value))

        if len(argument_list) != 0:
            method = u'%s(%s)' % (self.method.name, ''.join(argument_list))
        else:
            method = u'%s()' % self.method.name

        if is_new:
            event_handler.add_event(u'%s initialized the state value of %s - %s to %s' %
                                    (self.device.mac_address,
                                     self.method.interface.name,
                                     method,
                                     self.value))
        else:
            event_handler.add_event(u'%s updated the state value of %s - %s to %s' %
                                    (self.device.mac_address,
                                     self.method.interface.name,
                                     method,
                                     self.value))

        schedules = self._is_triggering()
        if schedules:
            event_handler.add_event('Device %s triggered configuration' %
                                    self.device.mac_address)
            logger.debug('Device %s triggered configuration' %
                         self.device.mac_address)
            signals.state_triggered.send(sender=self,
                                         device=self.device,
                                         schedules=schedules)


class StateValueArgument(Base):
    """A Django model class for state value arguments.

    In other words, this class is used to store the method arguments for
    specific method values. For instance, for a method eventApproaching(eid),
    the state value argument is eid and it can have an integer value, e.g., 10.

    Class attributes:
        * value: A Django :class:`CharField
          <django.db.models.CharField>` object for storing the value of a
          method argument.
        * state_value: A Django :class:`ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          a :class:`StateValue` object.
        * method_parameter: A Django :class:`ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          a :class:`MethodParameter` object.

    """
    value = models.CharField(max_length=255)
    state_value = models.ForeignKey(StateValue)
    method_parameter = models.ForeignKey(MethodParameter)

    class Meta:
        unique_together = ("state_value", "method_parameter")

    def __unicode__(self):
        """Return a string representation of the :class:`StateValueArgument`
        object."""
        return u'%s - %s = %s' % (self.state_value.method.name,
                                  self.method_parameter.name,
                                  self.value)


class Action(Base):
    """A Django model class for actions.

    Class attributes:
        * name: A Django :class:`CharField <django.db.models.CharField>` object
          for storing the name of the action.
        * precondition_expression: A Django :class:`CharField
          <django.db.models.CharField>` object for storing the precondition
          expression of the action. For instance, ``? and (? or ?)``.
        * action_file: A Django :class:`FileField
          <django.db.models.FileField>` object for storing the action file that
          defines the action.

    """
    name = models.CharField(max_length=255, unique=True)
    precondition_expression = models.CharField(max_length=500)
    action_file = models.FileField(upload_to='actions',
                                   max_length=100,
                                   null=True,
                                   blank=True)

    def __unicode__(self):
        """Return a string representation of the :class:`Action` object."""
        return self.name

    def save(self, *args, **kwargs):
        """Save the :class:`Action` object."""
        is_new = False
        if not self.id:
            is_new = True
        else:
            try:
                # The following lines should be in a transaction, so that an
                # action object is not updated with an action file between the
                # check and the delete
                with transaction.commit_on_success():
                    action = Action.objects.get(id=self.id)

                    # If the action file has changed and no other Action object
                    # references the old file, then delete the old one, because
                    # Django does not overwrite the old file and leaves it
                    # orphaned on the file system
                    if (action.action_file != self.action_file and
                        not (Action.objects
                                   .filter(action_file=action.action_file)
                                   .exclude(id=self.id)
                                   .exists())):
                        action.action_file.delete()
            except:
                pass

        super(Action, self).save(*args, **kwargs)

        if is_new:
            event_handler.add_event(u'Action %s added' % self.name)

# Connect a post delete signal with the deletion of action files
post_delete.connect(signals.delete_files, sender=Action)


class Trigger(Base):
    """A Django model class for triggers.

    Methods can be triggers and the triggering event occurs, when the value of
    the method is updated (or created) despite of the value.

    Class attributes:
        * method: A Django :class:`ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          a :class:`Method` object.

    """
    method = models.ForeignKey(Method, unique=True)

    def __unicode__(self):
        """Return a string representation of the :class:`Trigger` object."""
        return u'%s - %s' % (self.method.interface.name, self.method.name)

    def save(self, *args, **kwargs):
        """Save the :class:`Trigger` object."""
        is_new = False
        if not self.id:
            is_new = True

        super(Trigger, self).save(*args, **kwargs)

        if is_new:
            event_handler.add_event(u'Trigger %s - %s added' %
                                    (self.method.interface.name,
                                     self.method.name))


class Schedule(Base):
    """A Django model class for schedules.

    Class attributes:
        * name: A Django :class`CharField
          <django.db.models.CharField>` object for storing the name of the
          schedule.
        * configuration_model_name: A Django `CharField
          <django.db.models.CharField>` object for storing the name of the
          configuration model related to the schedule.
        * configuration_model_file: A Django `FileField
          <django.db.models.FileField>` object for storing the configuration
          model file that contains the configuration model for the schedule.
        * schedule_file: A Django `FileField
          <django.db.models.FileField>` object for storing the schedule file
          that defines the schedule.
        * trigger: A Django `ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          a :class:`Trigger` object.
        * actions: A Django `ManyToManyField
          <django.db.models.ManyToManyField>` object for storing a many-to-many
          relationship to :class:`Action` objects.

    """
    name = models.CharField(max_length=255, unique=True)
    configuration_model_name = models.CharField(max_length=255)
    configuration_model_file = models.FileField(upload_to='configuration_models',
                                                max_length=100,
                                                null=True,
                                                blank=True)
    schedule_file = models.FileField(upload_to='schedules',
                                     max_length=100,
                                     null=True,
                                     blank=True)
    trigger = models.ForeignKey(Trigger)
    actions = models.ManyToManyField(Action, through='ScheduleAction')

    def __unicode__(self):
        """Return a string representation of the :class:`Schedule` object."""
        return self.name

    def save(self, *args, **kwargs):
        """Save the :class:`Schedule` object."""
        is_new = False
        if not self.id:
            is_new = True
        else:
            try:
                # The following lines should be in a transaction, so that a
                # schedule object is not updated with a schedule file between
                # the check and the delete
                with transaction.commit_on_success():
                    schedule = Schedule.objects.get(id=self.id)

                    # If the schedule file has changed and no other Schedule
                    # object references the old file, then delete the old one,
                    # because Django does not overwrite the old file and leaves
                    # it orphaned on the file system
                    if (schedule.schedule_file != self.schedule_file and
                        not (Schedule.objects
                                     .filter(schedule_file=schedule.schedule_file)
                                     .exclude(id=self.id)
                                     .exists())):
                        schedule.schedule_file.delete()
            except:
                pass

        super(Schedule, self).save(*args, **kwargs)

        if is_new:
            event_handler.add_event(u'Schedule %s added' % self.name)

            # Send signal
            signals.schedule_added.send(sender=self, schedule=self)

# Connect a post delete signal with the deletion of schedule files
post_delete.connect(signals.delete_files, sender=Schedule)


class ActionDevice(Base):
    """A Django model class for action devices.

    An action device is, basically, a device that has been defined in an action
    file. For instance, the following action precondition contains two action
    devices, d1 and d2::

        @actionprecondition
        def precondition(self, d1, d2, eid):
            return misc.proximity([d1, d2]) and \
                d1.calendarSource.eventApproaching(eid) and \
                d1.hasInterface(TalkingDevice) and \
                d1.hasInterface(CalendarSource) and \
                d2.hasInterface(TalkingDevice)

    In the above example, action device d1 implements interfaces TalkingDevice
    and CalendarSource. Action device d1, on the other hand, implements only
    the TalkingDevice interface.

    Class attributes:
        * name: A Django `CharField
          <django.db.models.CharField>` object for storing the name of the
          action device as defined in the action file, e.g., ``d1``.
        * parameter_position: A Django `SmallIntegerField
          <django.db.models.SmallIntegerField>` object for storing the integer
          position of the action device in the action file's precondition
          parameters.
        * action: A Django `ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          a :class:`Action` object.
        * interfaces: A Django `ManyToManyField
          <django.db.models.ManyToManyField>` object for storing a many-to-many
          relationship to :class:`Interface` objects.

    """
    name = models.CharField(max_length=255)
    parameter_position = models.SmallIntegerField()
    action = models.ForeignKey(Action)
    interfaces = models.ManyToManyField(Interface,
                                        through='ActionDeviceInterface')

    class Meta:
        unique_together = (("action", "name"),
                           ("action", "parameter_position"),)

    def __unicode__(self):
        """Return a string representation of the :class:`ActionDevice`
        object."""
        return u'%s - %s' % (self.action.name, self.name)


class ScheduleAction(models.Model):
    """A Django model class for schedule-action relationships.

    Class attributes:
        * schedule: A Django `ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          a :class:`Schedule` object.
        * action: A Django `ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          a :class:`Action` object.
        * trigger_device: A Django `ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          an :class:`ActionDevice` object.
        * created_at: A Django `DateTimeField
          <django.db.models.DateTimeField>` object for storing the creation
          date and time of the schedule-action relationship.

    """
    schedule = models.ForeignKey(Schedule)
    action = models.ForeignKey(Action)
    trigger_device = models.ForeignKey(ActionDevice, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = ("schedule", "action")

    def __unicode__(self):
        """Return a string representation of the :class:`ScheduleAction`
        object."""
        return u'%s - %s' % (self.schedule.name, self.action.name)

    def save(self, *args, **kwargs):
        """Save the :class:`ScheduleAction` object."""
        is_new = False
        if not self.id:
            is_new = True

        super(ScheduleAction, self).save(*args, **kwargs)

        if is_new:
            event_handler.add_event(u'Action %s added for schedule %s' %
                                    (self.action.name, self.schedule.name))


class ActionDeviceInterface(models.Model):
    """A Django model class for the relationship between action devices and
    interfaces.

    Class attributes:
        * action_device: A Django `ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          an :class:`ActionDevice` object.
        * interface: A Django `ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          an :class:`Interface` object.
        * created_at: A Django `DateTimeField
          <django.db.models.DateTimeField>` object for storing the creation
          date and time of the relationship between the action device and the
          interface.

    """
    action_device = models.ForeignKey(ActionDevice)
    interface = models.ForeignKey(Interface)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = ("action_device", "interface")

    def __unicode__(self):
        """Return a string representation of the :class:`ActionDeviceInterface`
        object."""
        return u'%s - %s' % (self.action_device.name, self.interface.name)


class ActionPreconditionMethod(Base):
    """A Django model class for action precondition methods.

    An action precondition method is a method that is tested in the
    precondition of an action. For example, in the following action
    precondition, ``eventApproaching`` is an action precondition
    method::

    @actionprecondition
        def precondition(self, d1, d2, eid):
            return misc.proximity([d1, d2]) and \
                d1.calendarSource.eventApproaching(eid) and \
                d1.hasInterface(TalkingDevice) and \
                d1.hasInterface(CalendarSource) and \
                d2.hasInterface(TalkingDevice)

    Class attributes:
        * expression_position: A Django `SmallIntegerField
          <django.db.models.SmallIntegerField>` object for storing the integer
          position of the precondition method in the precondition expression.
          For example, ``eventApproaching`` is the first and only precondition
          method in the above example. Thus, its expression position is 0.
        * action: A Django `ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          an :class:`Action` object.
        * action_device: A Django `ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          an :class:`ActionDevice` object.
        * method: A Django `ForeignKey
          <django.db.models.ForeignKey>` object for storing the relationship to
          a :class:`Method` object.

    """
    expression_position = models.SmallIntegerField()
    action = models.ForeignKey(Action)
    action_device = models.ForeignKey(ActionDevice)
    method = models.ForeignKey(Method)

    class Meta:
        unique_together = ("action", "expression_position")

    def __unicode__(self):
        """Return a string representation of the
        :class:`ActionPreconditionMethod` object."""
        return u'%s - %i - %s.%s()' % (self.action.name,
                                       self.expression_position,
                                       self.action_device.name,
                                       self.method.name)


class ActionParameter(Base):
    action = models.ForeignKey(Action)
    name = models.CharField(max_length=255)
    parameter_position = models.SmallIntegerField()

    class Meta:
        unique_together = (("action", "name"),
                           ("action", "parameter_position"),)

    def __unicode__(self):
        return u"{0} - {1}".format(self.action.name,
                                   self.name)

from core.clients import MirriClient, MirriConnectionError, MirriTimeoutError, \
    MirriNotFoundError, CaasClient, CaasConnectionError, CaasTimeoutError, \
    CaasNotFoundError, CaasInternalServerError
from core.configuration_models import KumbangModelGenerator, WcrlModelGenerator
from django.core.files.base import ContentFile
from events.event import EventHandler
from profiler.decorators import profile
from kurre.settings import *
import logging
import models

logger = logging.getLogger(__name__)
event_handler = EventHandler()

@profile
def start_kumbang_configuration_task(device, schedules):
    logger.debug( "Starting configuration: self.schedules: %r" % (schedules) )

    # TODO Send post to CAAS
    # Get all devices in the same proximity group as the device
    #devices =
    #kbser = util.KumbangService( "http://caas.soberit.hut.fi", "KumbangConfigurator" )
    #for sched in self.schedules:
    #    kbser.generateModel( sched )

    # Get the precondition methods that are related to the actions in the schedules        
    # Requires optimization
    methods = {}               
    for sched in schedules:          
        actions = sched.actions.all() #scheduleaction_set.filter(schedule=sched) #models.ScheduleAction.objects.filter( schedule = sched )
        for act in actions:
            apm = models.ActionPreconditionMethod.objects.filter(action = act)

            for a in apm:
                if not a.method.interface.name in methods:
                    methods[a.method.interface.name] = [a.method.id]
                elif not a.method.id in methods[a.method.interface.name]:
                    methods[a.method.interface.name].append(a.method.id)
        
        for act in actions:
            #fill with interfaces, which have no precondition methods
            action_devices = act.actiondevice_set.all()
            for action_device in action_devices:
                action_device_interfaces = list(action_device.interfaces.all())
                for adi in action_device_interfaces:
                    if not adi.name in methods.keys():
                        logger.debug("appending empty (no precond. methods interface with nane: %s to the methods structure" %adi.name)
                        methods[adi.name] = []
    
    event_handler.add_event(u'Configuration methods %s' % (str(methods)))
    logger.debug(u'Aquired configuration methods: %r' % str(methods))

    devices = list(set(models.Device.objects.filter(interfaces__name__in=methods.keys()))) #.annotate(num_interfaces=Count('id')).filter(num_interfaces<=len(methods.keys()))

    event_handler.add_event(u'Configuration devices: %s' % str(devices))
    logger.debug(u'Configuration devices: %r' % devices)

    prox_devices = list(device.get_proximity_devices())
    prox_devices.append(device)
    event_handler.add_event(u'Configuration prox_devices: %r' % prox_devices)
    logger.debug(u'Configuration prox_devices: %r' % prox_devices)
    
    
    # Get the selections for the configuration
    configuration_model_name = ''
    selections = []
    
    for schedule in schedules:
        configuration_model_name += schedule.configuration_model_name
    
    for device in devices:
        mac_address = device.mac_address.replace(":", "_")
        attribute_name = 'isInProximity_%s' % mac_address
        value = "true" if device in prox_devices else "false"
        selections.append({'name': attribute_name, 'value': value})
        
        for interface in methods.keys():
            for m in methods[interface]:
                attribute_name = '%s_%s' % (models.Method.objects.get(id=m).name, mac_address)
                value = "true" if models.StateValue.objects.filter(device=device.id, method=m, value="True").exists() else "false"
                selections.append({'name': attribute_name, 'value': value})
    
    # Send configuration selections to Caas
    client = CaasClient()
    try:
        response = client.get_configuration(configuration_model_name, selections)
    except (CaasConnectionError, CaasTimeoutError, CaasNotFoundError, CaasInternalServerError), e:
        logger.error('The request to Caas failed: %s' % e)
        event_handler.add_event('The request to Caas failed: %s' % e)
    else:
        event_handler.add_event('Configuration request for model %s with selections %r sent to Caas' % (configuration_model_name, selections))
        configuration = response
    
        logger.debug(configuration)
    
    
        action_name = configuration['action_name']
        mirri_payload = []
        argument_values = []
        
        device_list = []
        for device in configuration['devices']:
            try:
                device_obj = models.Device.objects.get(mac_address=device['mac_address'])
            except models.Device.DoesNotExist:
                logger.error('Device %s does not exist' % mac_address)
            else:
                device_list.append({'device_obj': device_obj, 'interfaces': device['interfaces'], 'trigger': device['trigger']})
        
        action_devices = models.ActionDevice.objects.filter(action__name=action_name).order_by('parameter_position')
        for action_device in action_devices:
            trigger_device = False
            action_device_interfaces = None
            
            if action_device.scheduleaction_set.all().exists():
                trigger_device = True
            else:
                action_device_interfaces = action_device.interfaces.all()
                
            for i, device in enumerate(device_list):
                implements_all_interfaces = True
                if not trigger_device:
                    for action_device_interface in action_device_interfaces:
                        if action_device_interface.name not in device['interfaces']:
                            implements_all_interfaces = False
                            break
                        
                if (implements_all_interfaces and not trigger_device) or (trigger_device and device['trigger']):
                    device_list.pop(i)
                    
                    device_obj = device['device_obj']
                    device_interfaces = []
                    for interface_name in device['interfaces']:
                        interface_name = interface_name[0].lower() + interface_name[1:]
                        device_interfaces.append(interface_name)
                    mirri_payload.append({'deviceIdentity': device_obj.mac_address, 'deviceName': device_obj.name, 'interfaceNames': device_interfaces})
                    
                    parameters = []
                    # Fetch possible state value parameters
                    precondition_methods = action_device.actionpreconditionmethod_set.all().order_by('expression_position')
                    for precondition_method in precondition_methods:
                        method_parameters = precondition_method.method.methodparameter_set.all()
                        for method_parameter in method_parameters:
                            parameters.append(method_parameter)
                    
                    for parameter in parameters:
                        try:
                            state_value_argument = models.StateValueArgument.objects.get(method_parameter=parameter, state_value__device=device_obj)
                        except models.StateValueArgument.DoesNotExist, e:
                            logger.error(e)
                        else:
                            argument_values.append(state_value_argument.value)
                    break
        
        mirri_payload.extend(argument_values)
            
        #logger.debug("mirri_payload %s, action_name %s" % (mirri_payload, action_name))

        if action_name != "":
            init_parameters = body_parameters = mirri_payload
            
            #logger.debug('Action %s payload: %r' % (action_name, mirri_payload))
            
            # Send post to Mirri
            client = MirriClient()
            try:
                response = client.start_action(action_name, init_parameters, body_parameters)
            except (MirriConnectionError, MirriTimeoutError, MirriNotFoundError), e:
                logger.error('The request to Mirri failed: %s' % e)
                event_handler.add_event('The request to Mirri failed: %s' % e)
            else:
                #set devices as reseved
#                action_devices = models.Device.objects.filter(mac_address__in=mirri_payload['device_ids'].keys())
#                for dev in action_devices:
#                    dev.is_reserved = True
#                    dev.save()
                event_handler.add_event('Action %s sent to Mirri' % action_name)
                logger.debug(response)
        else:
            event_handler.add_event(u'No action was started' )
            logger.debug('No action was started')

    logger.debug( 'Configuration thread done' )
        
    
        
        
        
def start_configuration_task(device, schedules):
    clang = CAAS['CONFIGURATOR']
    
    if clang == 'wcrl':
        logger.error( 'NOT IMPLEMENTED')
    else:
        start_kumbang_configuration_task(device, schedule)
        
            
            
            
            


@profile
def generate_model(schedule):
    clang = CAAS['CONFIGURATOR']

    try:
        if clang == 'wcrl':
            model_suffix = '.lp'
            model_generator = WcrlModelGenerator()
        else:
            model_suffix = '.kbm'
            model_generator = KumbangModelGenerator()

        model = model_generator.generate_configuration_model(schedule)
    except Exception, e:
        logger.error(e)
    else:
        try:
            schedule.configuration_model_file.save('%s%s' % (schedule.name, model_suffix), ContentFile(model))
            schedule.configuration_model_name = schedule.name
            schedule.save()
            
            event_handler.add_event(u'%s model generated for schedule %s' % (string.capitalize(clang), schedule.name))
        except Exception, e:
            logger.error(e)
        else:
            # Send configuration model to Caas
            client = CaasClient()
            try:
                client.upload_configuration_model(schedule.name, model)
            except (CaasConnectionError, CaasTimeoutError, CaasNotFoundError, CaasInternalServerError), e:
                logger.error('The request to Caas failed: %s' % e)
                event_handler.add_event('The request to Caas failed: %s' % e)
            else:
                logger.debug('Configuration model %s sent to Caas' % schedule.name)

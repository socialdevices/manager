from core.tasks import generate_model, start_configuration_task
from django.db import transaction
from django.dispatch import Signal
import core.models
import logging
import threading

logger = logging.getLogger(__name__)

state_triggered = Signal(providing_args=["device", "schedules"])
schedule_added = Signal(providing_args=["schedule"])
#device_added = Signal(providing_args=["device"])
#device_deleted = Signal(providing_args=["device"])
device_interface_added = Signal(providing_args=["device", "interface"])
#device_interface_deleted = Signal(providing_args=["device", "interface"])


def start_configuration(sender, **kwargs):
    t = threading.Thread(target=start_configuration_task, args=(kwargs['device'], kwargs['schedules'],))
    t.start()

def generate_configuration_model(sender, **kwargs):
    t = threading.Thread(target=generate_model, args=(kwargs['schedule'],))
    t.start()
    #GenerateConfigurationModelThread(kwargs['schedule']).start()

def update_configuration_models(sender, **kwargs):
    # A new thread could also be done for the update of all models...
    schedules = core.models.Schedule.objects.all()
    
    for schedule in schedules:
        t = threading.Thread(target=generate_model, args=(schedule,))
        t.start()
        #GenerateConfigurationModelThread(schedule).start()

def delete_files(sender, instance, **kwargs):
    if isinstance(instance, core.models.Interface):
        interface = instance
        
        if interface.interface_file != None:
            # The following lines should be in a transaction, so that an interface object
            # is not updated with an interface file between the check and the delete
            with transaction.commit_on_success():
                # If no other Interface object references the old file, then delete the 
                # old one, because Django does not delete the old file and leaves it orphaned 
                # on the file system
                if not core.models.Interface.objects.filter(interface_file=interface.interface_file).exclude(id=interface.id).exists():
                    try:
                        # Save has to be false, since this function is called after an objects has been deleted
                        # and we don't want the object to be created again.
                        interface.interface_file.delete(save=False)
                    except Exception, e:
                        logger.error(e)
    elif isinstance(instance, core.models.Action):
        action = instance
        
        if action.action_file != None:
            # The following lines should be in a transaction, so that an action object
            # is not updated with an action file between the check and the delete
            with transaction.commit_on_success():
                # If no other Action object references the old file, then delete the 
                # old one, because Django does not delete the old file and leaves it orphaned 
                # on the file system
                if not core.models.Action.objects.filter(action_file=action.action_file).exclude(id=action.id).exists():
                    try:
                        # Save has to be false, since this function is called after an objects has been deleted
                        # and we don't want the object to be created again.
                        action.action_file.delete(save=False)
                    except Exception, e:
                        logger.error(e)
    elif isinstance(instance, core.models.Schedule):
        schedule = instance
        
        if schedule.schedule_file != None or schedule.configuration_model_file != None:
            # The following lines should be in a transaction, so that a schedule object
            # is not updated with a schedule file between the check and the delete
            with transaction.commit_on_success():
                # If no other Schedule object references the old file, then delete the 
                # old one, because Django does not delete the old file and leaves it orphaned 
                # on the file system
                if not core.models.Schedule.objects.filter(schedule_file=schedule.schedule_file).exclude(id=schedule.id).exists():
                    try:
                        # Save has to be false, since this function is called after an objects has been deleted
                        # and we don't want the object to be created again.
                        schedule.schedule_file.delete(save=False)
                    except Exception, e:
                        logger.error(e)
                
                if not core.models.Schedule.objects.filter(schedule_file=schedule.configuration_model_file).exclude(id=schedule.id).exists():
                    try:
                        # Save has to be false, since this function is called after an objects has been deleted
                        # and we don't want the object to be created again.
                        schedule.configuration_model_file.delete(save=False)
                    except Exception, e:
                        logger.error(e)
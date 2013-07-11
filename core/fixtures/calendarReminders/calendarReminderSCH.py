'''
Created on Dec 9, 2011

@author: t4aalton
'''
from socialDevices.deviceInterfaces.calendarSource import EventApproaching
from calendarReminders.fakeCall import FakeCall
from calendarReminders.conversation import Conversation
from socialDevices.misc  import AnyValue
import socialDevices.scheduling as scheduling
from socialDevices.scheduling import schedulingFunction

        
# Scheduling function takes a triggering event as its parameter, and returns
# am array of action instances.
@schedulingFunction
def calendarReminder(triggeringEvent):

    triggerFrom = triggeringEvent.messFrom
    triggerEid = triggeringEvent.eid
    
    fc = FakeCall(triggerFrom, AnyValue(), triggerEid)
    conv = Conversation(triggerFrom, AnyValue(), AnyValue(), triggerEid)
    return [fc, conv]

    
       
    
if __name__ == "__main__":
    
    ea = EventApproaching(10, 20)
    scheduling.addSchedule(EventApproaching, calendarReminder)
    print scheduling.getSchedule(EventApproaching)(ea)
  


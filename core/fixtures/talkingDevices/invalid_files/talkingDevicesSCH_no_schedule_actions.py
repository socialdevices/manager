'''
Created on Dec 14, 2011

@author: t4aalton
'''
from socialDevices.deviceInterfaces.talkingDevice import IsSilent
from talkingDevices.conversationOfThree import ConversationOfThree
from talkingDevices.dialog import Dialog
from socialDevices.misc  import AnyValue
import socialDevices.scheduling as scheduling
from socialDevices.scheduling import schedulingFunction

# Scheduling function takes a triggering event as its parameter, and returns
# am array of action instances.
@schedulingFunction
def talkingDevicesSCH(triggeringEvent):

    triggerFrom = triggeringEvent.messFrom

    d = Dialog(triggerFrom, AnyValue())
    cof = ConversationOfThree(triggerFrom, AnyValue(), AnyValue())

    return []

if __name__ == "__main__":

    scheduling.addSchedule(IsSilent, talkingDevicesSCH)
    

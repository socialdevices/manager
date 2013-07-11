'''
Created on Dec 16, 2011

@author: t4aalton
'''
from socialDevices.action import Action, actionprecondition, actionbody
from socialDevices.deviceInterfaces.talkingDevice import TalkingDevice
from socialDevices.deviceInterfaces.calendarSource import CalendarSource
import socialDevices.misc as misc
import random
   

class Conversation(Action):
    def __init__(self, source, d2, d3, eid):
        self.source = source
        self.d2 = d2
        self.d3 = d3
        self.eid = eid
    
    @actionprecondition
    def precondition(self, source, d2, d3, eid):
        return misc.proximity([source, d2, d3]) and source.talkingDevice.isWilling() and source.calendarSource.eventApproaching(eid) \
             and source.hasInterface(CalendarSource) and d2.hasInterface(TalkingDevice) and d3.hasInterface(TalkingDevice)
            
    @actionbody
    def body(self, source, d2, d3, eid):
        ce = source.calendarSource.getCalendarEvent(eid);
        d2.talkingDevice.say("Hey " + d3.getName() + " psst!");
        d3.talkingDevice.say("What?");
        d2.talkingDevice.say("Should we tell him that he  should be in " + ce.location + " soon?")
        if random.randint(1,2):
            d3.talkingDevice.say("Sure, we should")
            source.talkingDevice.say("I heard that!")
        else:
            misc.smalltalk(d2, d3)


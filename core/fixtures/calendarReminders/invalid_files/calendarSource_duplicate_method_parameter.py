'''
Created on Dec 1, 2011

@author: t4aalton
'''
from socialDevices.device import precondition, body, deviceInterface
import time
from socialDevices.misc import TriggeringEvent

class CalendarEvent:
    def __init__(self, eid, subject, location, time):
        self.eid = eid
        self.subject = subject
        self.location = location
        self.time = time

class EventApproaching(TriggeringEvent):
    def __init__(self, f, t):
        TriggeringEvent.__init__(self, f)
        #super(EventApproaching, self).__init__(f)
        self.eid = t
        

@deviceInterface
class CalendarSource():
    def __init__(self):
        currentTime = time.time()
        self.events = [CalendarEvent(0, 'weekly meeting', 'H5', currentTime - 1*600),
                       CalendarEvent(1, 'super meeting', 'Rower', currentTime + 10 * 600),
                       CalendarEvent(3, 'nice meeting', 'home', currentTime + 15 * 600)]
    
    @body
    def getCalendarEvent(self, eid):
        return self.events[eid]

    @precondition
    def eventApproaching(self, eid, eid):
        currentTime = time.time()
        event = self.events[eid]
        return event.time >= currentTime and event.time <= currentTime + 10*600
#        currentTime = time.time()
#        for event in self.events:
#            if event.time >= currentTime and event.time <= currentTime + 10*600:
#                return event.eid
#        return -1
    

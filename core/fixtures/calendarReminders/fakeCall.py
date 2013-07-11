'''
Created on Dec 16, 2011

@author: t4aalton
'''
from socialDevices.device import Device
from socialDevices.action import Action, actionprecondition, actionbody
from socialDevices.deviceInterfaces.talkingDevice import TalkingDevice
from socialDevices.deviceInterfaces.calendarSource import CalendarEvent, CalendarSource
import socialDevices.misc as misc
import random, time

class FakeCall(Action):
    def __init__(self, d1, d2, eid):
        self.d1 = d1
        self.d2 = d2
        self.eid = eid
        
        
    @actionprecondition
    def precondition(self, d1, d2, eid):
        return misc.proximity([d1, d2]) and d1.calendarSource.eventApproaching(eid) and d1.hasInterface(TalkingDevice) and \
            d1.hasInterface(CalendarSource) and d2.hasInterface(TalkingDevice)

    @actionbody
    def body(self, d1, d2, eid):
        ce = d1.calendarSource.getCalendarEvent(eid)
        if misc.synchronizeClocks([d1, d2]): #synching clocks sets strict timing to sync execution
            delay = '<break>' # this is speech synthesis markup language

            #d1.play(ringingSound) || d2.play(callerRingingSound)
            #misc.synchronize([d1.play, d2.play], [('ringing',),('callerRinging',)])
            #misc.synchronize2([d1.play, ('ringing',), d2.play, ('callerRinging',)])
            
            misc.startSync()
            d1.talkingDevice.play('ringing')
            d2.talkingDevice.play('callerRinging')
            misc.endSync()
        
            misc.startSync()
            d1.talkingDevice.say(d1.getName())
            d2.talkingDevice.say(delay + d1.getName(), 'metallic')
            misc.endSync()
            
            misc.startSync()
            d1.talkingDevice.say(d1.getName())
            d2.talkingDevice.say(delay + d1.getName(), filter = 'metallic')
            misc.endSync()
            
            gmMoment = time.gmtime(ce.time)
            momentString = str(gmMoment.tm_hour) + ':' + str(gmMoment.tm_min)
            sentence = 'Do not forget ' + ce.subject + ' in ' + ce.location + ' at ' + momentString
            misc.startSync()
            d2.talkingDevice.say(sentence)
            d1.talkingDevice.say(delay + sentence, filter = 'metallic');
            misc.endSync()

            answers = ['Thanks for remainding.', 'No I do not.', 'Of course not.']
            answer = random.choice(answers)
            misc.startSync()
            d1.talkingDevice.say(answer)
            d2.talkingDevice.say(delay + answer, filter = 'metallic')
            misc.endSync()



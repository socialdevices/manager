'''
Created on Dec 16, 2011

@author: t4aalton
'''
from socialDevices.action import Action, actionbody, actionprecondition
from socialDevices.deviceInterfaces.talkingDevice import TalkingDevice
from socialDevices.device import Device

import socialDevices.misc as misc

class ConversationOfThree(Action):
    def __init__(self, d1, d2, d3):
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
    
    @actionprecondition
    def precondition(self, d1, d2, d3):
        return misc.proximity([d1, d2, d3]) and d1.talkingDevice.isWilling() and d2.talkingDevice.isWilling() and d3.talkingDevice.isWilling() and d1.talkingDevice.isSilent() and \
            d1.hasInterface(TalkingDevice) and d2.hasInterface(TalkingDevice) and d3.hasInterface(TalkingDevice)

    @actionbody
    def body(self, d1, d2, d3):
        mtalk = misc.Mtalk()
        conversation = mtalk.getConversation(nbrOfPeople=3)
        devices = [d1, d2, d3]
        for line in conversation:
            devices[line[0]].talkingDevice.say(line[1])


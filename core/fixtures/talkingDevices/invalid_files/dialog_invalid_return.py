'''
Created on Dec 16, 2011

@author: t4aalton
'''
from socialDevices.action import Action, actionbody, actionprecondition
from socialDevices.deviceInterfaces.talkingDevice import TalkingDevice
from socialDevices.device import Device

import socialDevices.misc as misc


class Dialog(Action):
    def __init__(self, d1, d2):
        self.d1 = d1
        self.d2 = d2
        
        
    @actionprecondition
    def precondition(self, d1, d2):
        return misc.proximity([d1, d2]) and d1.talkingDevice.isWilling and d2.talkingDevice.isWilling() and d1.talkingDevice.isSilent() and \
            d1.hasInterface(TalkingDevice) and d2.hasInterface(TalkingDevice)
    
    @actionbody
    def body(self, d1, d2):
        mtalk = misc.Mtalk()
        conversation = mtalk.getConversation(nbrOfPeople=2)
        devices = [d1, d2]
        for line in conversation:
            devices[line[0]].talkingDevice.say(line[1])



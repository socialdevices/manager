'''
Created on Nov 3, 2011

@author: t4aalton
'''
from socialDevices.device import precondition, body, deviceInterface
from socialDevices.misc import TriggeringEvent

class IsSilent(TriggeringEvent):
    def __init__(self, f):
        super(IsSilent, self).__init__(f)


@deviceInterface
class TalkingDevice():
    
    def __init__(self):
        self.willing = False
        self.silent = True
#        self.temp = 0

    @body
    def say(self, str, filter='normal'):
        print(self.myDevice.getName() + ' (with ' + filter + ' voice): ' + str)
    
    
    @body
    def play(self, soundFile):
        print(self.myDevice.getName() + ': play(' + soundFile + ')')   
         
    @precondition
    def isWilling(self):
        return self.willing

    def setWilling(self):
        self.willing = True
        
    def setUnwilling(self):
        self.willing = False

    @precondition
    def isSilent(self):
        return self.silent
        
    def setSilence(self):
        self.silent = True
        
    def setUnsilence(self):
        self.silent = False


@deviceInterface
class TalkingDevice2():
    
    def __init__(self):
        self.willing = False
        self.silent = True
#        self.temp = 0

    @body
    def say(self, str, filter='normal'):
        print(self.myDevice.getName() + ' (with ' + filter + ' voice): ' + str)
    
    
    @body
    def play(self, soundFile):
        print(self.myDevice.getName() + ': play(' + soundFile + ')')   
         
    @precondition
    def isWilling(self):
        return self.willing

    def setWilling(self):
        self.willing = True
        
    def setUnwilling(self):
        self.willing = False

    @precondition
    def isSilent(self):
        return self.silent
        
    def setSilence(self):
        self.silent = True
        
    def setUnsilence(self):
        self.silent = False

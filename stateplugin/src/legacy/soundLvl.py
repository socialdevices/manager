
import sound
import threading, time

class SoundLvl( threading.Thread ):

    def init( self, stateClient ):
        self.driver = sound.MicDriver()
        self.stateClient = stateClient

        self.isSilent = False
        
        self.is_running = False

    def run( self ):
        self.is_running = True
        while self.is_running:
            lvl = self.driver.read()
            #print 'Ambient sound is %s'%('high', 'low')[lvl]
            if lvl != self.isSilent:
                self.stateClient.add_state_event( 'TalkingDevice', 'isSilent', str(lvl) )
                self.isSilent = lvl
            #print 'micdriver sleeping 10'
            time.sleep(10)

    def stop(self):
        print "Stopping SoundLvl"
        self.is_running = False


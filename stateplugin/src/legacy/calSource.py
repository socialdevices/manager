
import calendar
import threading, time

class CalSource( threading.Thread ):

    def init( self, stateClient ):
        self.driver = calendar.SQLiteCalDriver()
        #self.conn = gui.conn
        #self.gui = gui
        self.stateClient = stateClient
        
        self.announced_ids = []
        self.is_running = False

    def run( self ):
        self.is_running = True
        self.driver.read_next()
        while self.is_running:
            try:
                if self.driver.nextevent == None or self.driver.nextevent[int(self.driver.properties['componentid'])] in self.announced_ids:
                    self.driver.cv.acquire();
                    #print "Waiting for new event"
                    self.driver.cv.wait()
                    #print "woke up"
                    self.driver.cv.release()

                else:
                    self.driver.cv.acquire()
                    t = self.driver.nextevent[int(self.driver.properties['datestart'])]
                    now = time.time()
                    #print "alarm time", t, "now:", now
                    
                    if self.driver.nextevent[int(self.driver.properties['componentid'])] not in self.announced_ids and t <= now:
                        self.stateClient.add_state_event( 'CalendarSource', 'eventApproaching', 'True', 'eid', "%i"%(self.driver.nextevent[int(self.driver.properties['componentid'])]))
            
                        self.announced_ids.append(self.driver.nextevent[int(self.driver.properties['componentid'])])
                        self.driver.read_next()
                    else:
                        #print "waiting %i secs" %( t-now )
                        self.driver.cv.wait( t-now )
                        #print "woke up"	
                        
                        self.driver.cv.release()

            except Exception, e:
                print "ee", e.message

    def stop(self):
        print "stopping CalSource"
        self.is_running = False
        self.driver.cv.acquire()
        self.driver.cv.notify_all()
        self.driver.cv.release()

        self.driver.stop()

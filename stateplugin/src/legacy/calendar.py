# KurreSS driver for sqlite3 calendar
from driver import Driver, DriverException
import simplejson as json
import kurreconfig
import pyinotify, sqlite3, time, threading


class PMailEvents( pyinotify.ProcessEvent ):
    

    
    def init(self, dispatch):
        self.dispatch = dispatch

    def process_IN_MODIFY(self, event):
        print "Calendar database changed, refreshing event info"
        self.dispatch()
        
        
class SQLiteCalDriver(Driver):
    def __init__(self, event_handler=None):
        self.properties = dict(kurreconfig.config.items("CalDriver"))
        self.cv = threading.Condition()
        self.nextevent = None
        #super(SQLiteCalDriver, self).__init__(self.properties)
        
        try:
            if event_handler == None:
                self.event_handler = PMailEvents()
                self.event_handler.init( self.read_next_notif )
            else:
                self.event_handler = event_handler
        
            self.wm = pyinotify.WatchManager()
            #print self.properties['path']
            self.wm.add_watch( self.properties['path'], pyinotify.IN_MODIFY )
        
            self.notifier = pyinotify.ThreadedNotifier( self.wm, self.event_handler )
            self.notifier.start()

        except Exception, e:
            raise DriverException( e.message )


    def stop(self):
        print "Stopping Calendar driver"
        self.notifier.stop()
        
        
    def read_next_notif(self):
        try:
            connection = sqlite3.connect(self.properties['path'])
        except:
            print "Error connecting to database"
        
        c = connection.cursor()

        c.execute('select * from Components order by DateStart')
        self.nextevent = None

        for row in c:
            #print row
            s = row[int(self.properties['datestart'])]
            if s > time.time():
                print row
                self.nextevent = row
                self.cv.acquire()
                self.cv.notifyAll()
                self.cv.release()
                break

        connection.close()


    def read_next(self):
        try:
            connection = sqlite3.connect(self.properties['path'])
        except:
            print "Error connecting to database"
        
        c = connection.cursor()

        c.execute('select * from Components order by DateStart')
    
        self.nextEvent = None

        for row in c:
            #print row
            s = row[int(self.properties['datestart'])]
            if s > time.time():
                #print row
                self.nextevent = row    
                break

        connection.close()	

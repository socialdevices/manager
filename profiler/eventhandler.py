import pyinotify

class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, condition):
        self.condition = condition
        
    def process_IN_CREATE(self, event):
        if event.pathname.endswith('.lock'):
            print 'Lock created: %s' % event.pathname
            #print "Creating:", event.pathname
    
    def process_IN_DELETE(self, event):
        if event.pathname.endswith('.lock'):
            with self.condition:
                print 'Lock removed: %s' % event.pathname
                self.condition.notifyAll()
                #print "Removing:", event.pathname
    
    def process_IN_MODIFY(self, event):
        #print "Modifying:", event.pathname
        pass
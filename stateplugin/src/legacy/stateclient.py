from connection import Connection
import threading
import calSource
import soundLvl
import gobject
from subprocess import Popen, PIPE

class StateClient(threading.Thread):

    def __init__(self, ownId, ownName=None, host=None, port=None):
        self.api_version="v2"
        
        print ownId, ownName, host, port
        
        self.eventq = []
        self.eventqc = threading.Condition()
        self.ownid = ownId

        if ownName == None:
            self.devName = 'default'
        else:
            self.devname = ownName

        if host == None:
            host = 'kurre.soberit.hut.fi'
        
        if port == None:
            port = '80'
            
        self.kurreClient = Connection(host, port)

        self.prefix = '/api/v2/device/'

        self.running=False
        
        self.micThread = soundLvl.SoundLvl()
        self.calThread = calSource.CalSource()
        
        self.calThread.init(self)
        self.micThread.init(self)

        self.add_state_event( 'TalkingDevice', 'isWilling', 'True' )

        threading.Thread.__init__(self)
        self.setDaemon(True)

                
    def set_printer(self, printer):    
        self.kurreClient.set_printer(printer)
        self.printer = printer
        
    def add_state_event(self, iface, method, value, arg_name=None, arg_val=None):
        #print 'add state event called, params:', iface, method, value, arg_name, arg_val
        self.eventqc.acquire()

        #form the method path
        method_path = self.ownid + '/interface/' + iface + '/method/' + method

        if arg_name == None:
            new_event = { "method": "PUT", "method_path": method_path, 'data': {'value':value} }
        else:
            new_event = { "method": "PUT", "method_path": method_path, 'data': {'value':value, 'arguments':{arg_name: arg_val}} }
        
        if new_event in self.eventq:
            pass
        else:
            self.eventq.append( new_event )

        self.eventqc.notify()
        self.eventqc.release()

    def run(self):
        self.running = True

        self.calThread.start()
        self.micThread.start()

        while self.running:
            #check for items in q
            self.eventqc.acquire()
            #print self.eventq
            for event in self.eventq:
                print 'processing event:', event
                #post for update, put for create
                if event['method'] == "PUT":
                    repl_status = self.kurreClient.put( self.prefix + event["method_path"] + '/', event["data"] )
                elif event['method'] == "POST":
                    repl_status = self.kurreClient.post( self.prefix + event["method_path"] + '/', event["data"] )
                #print 'repl status', repl_status
                if isinstance(repl_status, Exception):
                    print repl_status
                    
                elif repl_status != 201 and repl_status != 204: 
                    apip_struct = event['method_path'].split('/')
                    if len(apip_struct) == 5: # we were making a state value update
                        method_name = apip_struct.pop()
                        method_path = '/'.join(apip_struct)
                        event['data']['method_name'] = method_name
                        event['method'] = "POST"
                        event['method_path'] = method_path
                        #print 'put failed, modified event added', event
                        # no need to update again with put, since creation updates value as well
                    elif len(apip_struct) == 4: # state value creation failed
                        # create the interface
                        iface_name = apip_struct[2]
                        method_path = self.ownid + '/interface'
                        data = {"interface_name": iface_name}
                        new_event = { 'method':'POST', 'method_path': method_path, 'data': data }

                        if new_event in self.eventq:
                            pass #no need to add
                        else:
                            self.eventq.append(new_event)
                        #print 'post failed, modified event added', new_event
                    elif len(apip_struct) == 3: # interface could not be created
                        method_path = self.prefix
                        data = { 'mac_address': self.ownid, "name": self.devname }
                        new_event = { 'method':'POST', 'method_path': method_path, 'data': data }
                        
                        if new_event in self.eventq:
                            pass
                        else:
                            self.eventq.append( new_event )
                            
                        
                else:
                    #print 'event', event, 'handled, removing.'
                    self.eventq.remove(event)
                    
                #print 'event processed'
                    
            if not self.eventq:
                #print 'eventq empty stateclient sleeping'
                self.eventqc.wait()
            else:
                print 'could not process all events, trying again in 5'
                self.eventqc.wait(5)
                
                
    def stop(self):
        #stop drivers
        print "Stopping StateClient"
        self.calThread.stop()
        self.micThread.stop()
        
        
        self.running = False
        self.eventqc.acquire()
        self.eventqc.notify()
        self.eventqc.release()

def sdQtMethod():
    global CURRENT_PLUGIN_WINGET
    CURRENT_PLUGIN_WINGET = QtGui.QWidget()
    CURRENT_PLUGIN_WINGET.resize(250, 150)
    CURRENT_PLUGIN_WINGET.setWindowTitle('StateClient Settings')
    CURRENT_PLUGIN_WINGET.show()
    return
                        
def sdInitPlugin(options, pluginManager):


    p = Popen(["ls","/var/lib/bluetooth"],stdout=PIPE)
    output = p.communicate()
    ownId = output[0].split("\n")[0].lower()

    stateClient = StateClient(ownId, options.device_callname, options.stateserver_uri, options.stateserver_port)
    
    return stateClient

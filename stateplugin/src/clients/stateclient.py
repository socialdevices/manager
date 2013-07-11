from connection import Connection
import threading
from subprocess import Popen, PIPE

class StateClient(threading.Thread):

    def __init__(self, ownId, ownName=None, host=None, port=None):
        self.api_version="v3"
        
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
            
        self.kurreClient = Connection(host, port, self.api_version)

        self.api = self.kurreClient.api_update( ownId )
        self.prefix = '/api/v3/devices/'

        self.running=False
        
        #self.add_state_event( 'TalkingDevice', 'isWilling', 'True' )

        threading.Thread.__init__(self)
        self.setDaemon(True)

                
    def set_printer(self, printer):    
        self.kurreClient.set_printer(printer)
        self.printer = printer
        
    def add_state_event(self, iface, method, value, arg_name=None, arg_val=None):
        #print 'add state event called, params:', iface, method, value, arg_name, arg_val
        self.eventqc.acquire()

        #form the method path
        for i in self.api:
            if iface in i.keys():
                for m in i['methods']:
                    if method in m.keys():
                        method_path = self.ownid + '/states/' + m[method]

        if arg_name == None:
            new_event = { "method": "PATCH", "method_path": method_path, 'data': {'value':value} }
        else:
            new_event = { "method": "PATCH", "method_path": method_path, 'data': {'value':value, 'arguments':{arg_name: arg_val}} }
        
        if new_event in self.eventq:
            pass
        else:
            self.eventq.append( new_event )

        self.eventqc.notify()
        self.eventqc.release()

    def run(self):
        self.running = True

        while self.running:
            #check for items in q
            self.eventqc.acquire()
            #print self.eventq
            for event in self.eventq:
                print 'processing event:', event
                #PATCH
                if event['method'] == "PATCH":
                    repl_status = self.kurreClient.patch( self.prefix + event["method_path"] + '/', event["data"] )
                elif event['method'] == "PATCH":
                    repl_status = self.kurreClient.patch( self.prefix + event["method_path"] + '/', event["data"] )

                if isinstance(repl_status, Exception):
                    print repl_status
                    
                elif repl_status != 201 and repl_status != 204 and repl_status != 202: 
                    apip_struct = event['method_path'].split('/')
                    if len(apip_struct) == 5: # we were making a state value update
                        method_name = apip_struct.pop()
                        method_path = '/'.join(apip_struct)
                        event['data']['method_name'] = method_name
                        event['method'] = "PATCH"
                        event['method_path'] = method_path
                        #print 'put failed, modified event added', event
                        # no need to update again with put, since creation updates value as well
                    elif len(apip_struct) == 4: # state value creation failed
                        # create the interface
                        iface_name = apip_struct[2]
                        method_path = self.ownid + '/interface'
                        data = {"interface_name": iface_name}
                        new_event = { 'method':'PATCH', 'method_path': method_path, 'data': data }

                        if new_event in self.eventq:
                            pass #no need to add
                        else:
                            self.eventq.append(new_event)
                        #print 'post failed, modified event added', new_event
                    elif len(apip_struct) == 3: # interface could not be created
                        method_path = self.prefix
                        data = { 'mac_address': self.ownid, "name": self.devname }
                        new_event = { 'method':'PATCH', 'method_path': method_path, 'data': data }
                        
                        if new_event in self.eventq:
                            pass
                        else:
                            self.eventq.append( new_event )
                            
                        
                else:
                    print 'event', event, 'handled, removing.'
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
        self.running = False
        self.eventqc.acquire()
        self.eventqc.notify()
        self.eventqc.release()

                    
def sdInitPlugin(options, updateManager, qtApp):

    from stateclient import StateClient

    p = Popen(["ls","/var/lib/bluetooth"],stdout=PIPE)
    output = p.communicate()
    ownId = output[0].split("\n")[0].lower()


    stateClient = StateClient(ownId, options.device_callname, options.stateserver_uri, options.stateserver_port)
    stateClient.start()

import sys
 
import PySide
from PySide.QtGui import *
from components.component import *
from components.source import *
from components.sink import *
from clients.stateclient import StateClient
import time

from threading import Thread
from time import sleep

from gui.base import *
from util.conf import *


from subprocess import Popen, PIPE

class StatePlugin(threading.Thread):
    
    
    def sdQtMethod(self):
        class StateRenderWidget(QtGui.QScrollArea):
            def __init__(self, statePlugin):
                super(StateRenderWidget, self).__init__()
                self.initUI()
                self.statePlugin = statePlugin
    
                self.mainw = QWidget(self)
                self.mainlayout = QVBoxLayout()    
    
            def initUI(self):
                self.iws = {}
                
                # create the ui system
                for interface in self.statePlugin.pipelines.keys():
                    methods=self.statePlugin.pipelines[interface].keys()
                    iw = InfoFrame( parent=mainw, name=interface )
                        
                    for method in methods: #these are the interface methods, essentially
                        methodw = InfoFrame( parent=iw, name=method, level=1 )
                        iw.addGuiElem(methodw)
                        
                        pipe_components = pipelines[interface][method]
                        
                        for comp in pipe_components:
                            compw = InfoFrame(parent=methodw, name=comp.name, level=2)
                            compw.addGuiElem(comp.initUi())
                            
                            methodw.addGuiElem(compw)
                            

                    self.mainlayout.addWidget(iw)
                    self.iws[interface] = iw


                # bind source states..
                for interface in sources.keys():
                    self.iws[interface].valueGuiElem.slider.valueChanged[int].connect( self.statePlugin.sources[interface].set_state )

                self.mainlayout.addStretch()
                self.mainw.setLayout( mainlayout )

                for iw in self.iws.keys():
                    iws[iw].showMethodElemsRecur(False)
                    
                self.setWidget(self.mainw)
            

        global CURRENT_PLUGIN_WINGET
        CURRENT_PLUGIN_WINGET = StateRenderWidget(self)
        CURRENT_PLUGIN_WINGET.show()
    
    
        return
    
    def __init__(self, ownId, ownName=None, host=None, port=None):

        self.capabilities = self.detectCapabilities()
        self.preconditions = capabilities['precondition']



        # create a test StateClient
        self.stateClient = StateClient( config.get('identity', 'id'), 
                                        config.get('identity', 'name'),
                                        config.get('server', 'address'),
                                        config.get('server', 'port') )
        self.stateClient.start()

        # create and connect pipelines
        self.pipelines = {}

        # test struct for source components
        self.sources = {}

        for interface in self.preconditions.keys():
            pipelines[interface] = {}
            methods=preconditions[interface]

            for method in methods.keys(): #these are the interface methods, essentially
                pipe = callPipe(methods[method])
                pipe_components = []

                if pipe and type(pipe) == list: #valid pipeline implementation expected here..
                    print pipe

                    for comp in pipe:
                        cclass = instantiateComponent(comp)
                        if cclass: pipe_components.append( cclass )

                        if type(cclass) == SimpleStateSink:
                            cclass.setEventMethod_callback( cb_test )
                        ##testing
                        elif type(cclass) == TrackerSource:
                            print "appending source Class: " + str(cclass)
                            self.sources[interface] = cclass

                    self.pipelines[interface][method] = pipe_components

                elif type(pipe) != list:
                    print "Pipe description missing: pipeline not created for:", interface, method
                else:
                    print "Pipeline description not found: pipeline not created"
                    
                self.connectPipeComponents( pipe_components )    




        

        threading.Thread.__init__(self)
        self.setDaemon(True)


    def run(self):
        self.running = True
        kk = True
        while self.running:
            print "worker ticking sources.."
            for source in self.sources.keys():
                self.sources[source].tick()

            print "done"
            #testing
            print 'adding state_event'
            
            stateClient.add_state_event( 'TalkingDevice', 'isSilent', str(kk) )
            kk = not kk
            
            sleep(10)
            
        self.stateClient.stop()
        
    def stop(self):
        self.running = False


    def detectCapabilities(self):
        body = {}
        precon = {}
        try:
            import capability
            from inspect import getmembers, isclass, ismethod

            for m in filter( lambda x: not x.startswith('__'), dir(capability) ):
                for c in getmembers( eval('capability.' + m), isclass ):
                    d_b = dict(getmembers(c[1],lambda x: ismethod(x) and 'SDMethodType' in dir(x) and x.SDMethodType == 'body'))
                    d_p = dict(getmembers(c[1],lambda x: ismethod(x) and 'SDMethodType' in dir(x) and x.SDMethodType == 'pre'))
                    if d_b:
                        if '__init__' in d_b.keys():
                            del d_b['__init__']
                        body[c[0]] = d_b
                    if d_p:
                        if '__init__' in d_p.keys():
                            del d_p['__init__']
                        precon[c[0]] = d_p

            #del getmembers, isclass, ismethod

        except Exception, x:
            print "Error detecting capabilities: "
            print str(x)

        return {'body':body, 'precondition':precon}

    def instantiateComponent(self, compDescr):
        instance = None
        if len( compDescr.keys() ) != 1:
            print "Component parse error: Multiple component definitions packed into single comp. TBD"
            return None
        else:
            for ccname in compDescr.keys():
                try:
                    # even though this is looped, should be only one component class in one.. looks cleaner this way..
                    insts_str = ccname + '( **' + str(compDescr[ccname]) + ' )' 
                    instance = eval( insts_str )    
                except Exception, e:
                    print "Error instantiating component" + ccname + ", caught: \n"
                    print str(e)
                    return None
        
        return instance

    def connectPipeComponents(self, pipe):
        print "connecting pipe", str(pipe)
        if pipe:
            print "pipe found" 
            prev = None       
            for c in pipe:
                #print "wtf c", c, " prev", prev
                if prev:
                    print prev.name, "connecting to", c.name
                    prev.connect_to(c)            
                prev = c
               
            # if the last component is a statesink, bind it to client
            print 'Type of the last components in pipe = {0}'.format( type(c) )
            if type(c) == SimpleStateSink:
                print "Connecting component " + c.name + " to stateClient"
                c.setEventMethod_callback( stateClient.add_state_event )

    def callPipe(self, method):
        try:
            from inspect import getargspec
            
            args = getargspec(method).args
            if args:
                call_args = [None] * (len(args)-1)
                return method(*call_args)
    
            return None
    
        except Exception, x:
            print "Error detecting capabilities: "
            print str(x)
            return None
                


class Tick( Thread ):
    def init(self, sources):
        self.sources = sources
        self.running = True
    
    
    def run(self):
        kk = True
        while self.running:
            print "worker ticking sources.."
            for source in self.sources.keys():
                self.sources[source].tick()

            print "done"
            #testing
            print 'adding state_event'
            
            stateClient.add_state_event( 'TalkingDevice', 'isSilent', str(kk) )
            kk = not kk
            
            sleep(10)
        
    def stop(self):
        self.running = False                
                
                





                        
def sdInitPlugin(options, pluginManager):
    p = Popen(["ls","/var/lib/bluetooth"],stdout=PIPE)
    output = p.communicate()
    ownId = output[0].split("\n")[0].lower()

    statePlugin = StatePlugin(ownId, options.device_callname, options.stateserver_uri, options.stateserver_port)
    
    return stateClient

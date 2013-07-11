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


def detectCapabilities():
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

def instantiateComponent( compDescr ):
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

def connectPipeComponents( pipe ):
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

def callPipe(method):
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


def cb_test(**kwargs):
    print str(kwargs)




# Create the application object
app = QApplication(sys.argv)

mainwin = QMainWindow()
mainwin.setWindowTitle('Mainview (plugins)')
#mainwin.setFixedWidth( QApplication.desktop().width()-20 )

sa = QScrollArea(mainwin)
#mainwin.setCentralWidget(sa)

mainw = QWidget(sa)
mainlayout = QVBoxLayout()



capabilities = detectCapabilities()
preconditions = capabilities['precondition']

# create a test StateClient
stateClient = StateClient( config.get('identity', 'id'), 
                           config.get('identity', 'name'),
                           config.get('server', 'address'),
                           config.get('server', 'port') )
stateClient.start()

# create and connect pipelines
pipelines = {}

# test struct for source components
sources = {}

for interface in preconditions.keys():
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
                    sources[interface] = cclass

            pipelines[interface][method] = pipe_components

        elif type(pipe) != list:
            print "Pipe description missing: pipeline not created for:", interface, method
        else:
            print "Pipeline description not found: pipeline not created"
            
        connectPipeComponents( pipe_components )    

#print str(pipelines)

iws = {}


# create the ui system
for interface in pipelines.keys():
    methods=pipelines[interface].keys()
    iw = InfoFrame( parent=mainw, name=interface )
        
    for method in methods: #these are the interface methods, essentially
        methodw = InfoFrame( parent=iw, name=method, level=1 )
        iw.addGuiElem(methodw)


        pipe_components = pipelines[interface][method]

        for comp in pipe_components:
            compw = InfoFrame(parent=methodw, name=comp.name, level=2)
            compw.addGuiElem(comp.initUi())
    
            methodw.addGuiElem(compw)
            

    mainlayout.addWidget(iw)
    iws[interface] = iw


## bind source states..
for interface in sources.keys():
    iws[interface].valueGuiElem.slider.valueChanged[int].connect( sources[interface].set_state )
    


mainlayout.addStretch()
mainw.setLayout( mainlayout )

sa.setWidget(mainw)


mainwin.setCentralWidget(sa)

mainwin.show()




for iw in iws.keys():
    iws[iw].showMethodElemsRecur(False)


comp_thread = Tick()
comp_thread.init(sources)

comp_thread.start()

app.aboutToQuit.connect( comp_thread.stop )

sys.exit(app.exec_())

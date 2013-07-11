###
# Base class for all of the pipeline components 
# tier 1 -> one input/one output all the
# Defines interfaces for input, output and the handle method
import PySide
import PySide.QtCore
from PySide.QtGui import *


class Component(PySide.QtCore.QObject):

    input_changed = PySide.QtCore.Signal()
    output_changed = PySide.QtCore.Signal()

    def __init__(self, name):
        super(Component, self).__init__()
        self.name = name
        self.input=None
        self.output=None
                
        self.receivers = []
    
        self.layout = None
        
        
        
    def connect_to(self, target_comp, target_input=None):
        self.receivers.append( target_comp.set_input )
        print self.name, "connected to", target_comp.name

    # disconnects all signals
    def disconnect(self):
        self.receivers = []
        
    # takes care of  triggering output, when result can be calculated ( needed for components with buffers inside )
    def set_input(self, val):    
        print self.name + ".set_input( " + str(val) + " )"
        self.input = val
        self.input_changed.emit()
        
        if self.signals_ready():
            self.handle()    
        
            self._propagate()
    
    def _propagate(self):
        for receiver in self.receivers:
            receiver( self.output )
        
    def signals_ready(self):
        return self.input != None

    def handle(self):
        #print self.name + ".handle"
        self.output = self.input

        self.output_changed.emit()        
        #send signal here..

    def update_output_label(self):
        print self.name, "updating output"
        self.outputLabel.setText(str(self.output))

    #does not add layout to the parent widgets layout, since this is meant to be overridden and called from child anyways..
    def initUi(self, parent_w = None):
        self.w = QFrame(parent_w)
        self.w.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.layout = QHBoxLayout()
 
 
        self.nameLabel = QLabel(self.w)
        self.nameLabel.setText( self.name )
        
        self.outputLabel = QLabel(self.w)
        self.update_output_label()
        self.output_changed.connect( self.update_output_label )
        
        
        self.layout.addWidget( self.nameLabel )
        self.layout.addWidget( self.outputLabel )
        
        self.w.setLayout( self.layout )
        return self.w

    def render(self):
        pass #nothing to do here, no ui components available


class SourceComp( Component ):
    def __init__(self, name, source=None):
        super(SourceComp, self).__init__(name)
        self.source = source
        
        self.state = 2
        
    def set_state(self, state):
        print self.name, "setting state:", state
        self.state = state
        
    def set_read(self, read_func):
        self.read = read_func
                
    def tick(self):
        print self.name, "tick"
        if self.state == 0:
            self.set_input(self.read())

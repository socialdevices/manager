##
# Classes for main components:
#  - Interface
#  

import PySide
from PySide.QtGui import QFrame
from PySide.QtGui import QPushButton
from PySide.QtGui import QSlider
from PySide.QtGui import QLabel
from PySide.QtGui import QHBoxLayout
from PySide.QtGui import QVBoxLayout

# helper class for slider with combined value label
class ActivationSlider( QFrame ): 
    def __init__(self, parent = None):
        super(ActivationSlider, self).__init__(parent)
        self.activation_states=['Automatic', 'Tentative', 'Disabled']

        self.initUi()
        
    def initUi(self):

        #slider
        slider = QSlider(PySide.QtCore.Qt.Orientation.Horizontal, self)
        slider.setRange(0,2)
        slider.setTickInterval(1)
        slider.setValue(2)
        self.slider = slider

        #.. and corresponding label element
        label = QLabel(self)
        label.setText(self.activation_states[slider.value()])
        self.label = label
        
        #connections
        #PySide.QtCore.QObject.connect(slider, slider.valueChanged, self, self.update_label)
        #self.connect(slider.valueChanged, self.update_label())
        slider.valueChanged[int].connect(self.update_label)
        
        # layout
        lo = QVBoxLayout() 
        lo.addWidget( slider )
        lo.addWidget( label )


        self.setLayout(lo)
        #self.l
        
    def update_label(self, value):
        #self.label.setText( self.activation_states[self.slider.value()] )
        self.label.setText( self.activation_states[value] )

class MethodValueLabel( QLabel ):
    def __init__( self, parent ):
        super( MethodValueLabel, self ).__init__( parent )

        self.setText('No value yet')
                
    def changeText( self, newText ):
        self.setText( newText )


class InfoFrame( QFrame ):
    def __init__(self, parent = None, name = None, level=0, customValueGui = None ):
        self.name = name
        super(InfoFrame, self).__init__(parent)
        
        #interface methods go here.. their visibility needs to be connected to the expansion button
        self.methodElems = []
        
        #level designates the value on the side of the name shown.. 0: top-level interface component
        self.level = level
        
        self.valueGuiElem = customValueGui
        
        # custom element to show within component
        #self.customValueGui = customValueGui
        
        self.initUi()
        
    def initUi(self):
        # button for interface expansion with name on it
        self.expButton = QPushButton(self.name, self)
        self.expButton.setCheckable(True)
        self.expButton.setChecked(False) #start unexpanded
        
        
        #level designates the value on the side of the name shown.. 
        # 0: top-level interface component
        # 1: method component
        # 2: custom value component (pipeline components, practically) Need to provide valueGuiElem on contructor.
        if self.level == 0:
            # slider for switching interface activity state, 3 states: active, tentative, disabled
            self.valueGuiElem = ActivationSlider(self)
        elif self.level == 1:
            self.valueGuiElem = MethodValueLabel(self)
        else:
            if self.valueGuiElem == None: 
                print "Warning: custom ui field empty, component level custom!"
        
        
        # connect the toggle signal to the expansion method
        self.expButton.toggled[bool].connect( self.showMethodElems )

        lo = QHBoxLayout()
            
        lo.addSpacing( self.level * 15 )    
        lo.addWidget( self.expButton )
        if self.valueGuiElem: lo.addWidget( self.valueGuiElem )
          
          
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(lo)
            
        self.setFrameStyle( QFrame.Box | QFrame.Raised )

        self.setLayout( mainLayout )
        


    def addGuiElem( self, elem ):
        self.methodElems.append( elem )
        self.layout().addWidget( elem )
        #self.expButton.toggled[bool].connect( elem.setVisible )


    def showMethodElems(self, toggled ):
        if toggled:
            for child in self.methodElems: 
                child.show()
        else:
            for child in self.methodElems: 
                child.hide()

    # recursively displays, or hides, the child elements..
    def showMethodElemsRecur(self, toggled ):
        for child in self.methodElems: 
            if toggled:
                child.show()
            else:
                child.hide()

            if type( child ) == InfoFrame:
                child.showMethodElemsRecur(toggled)
        

from base import Component
import operator
from datetime import datetime



##
# Adds two signals together
class Adder( Component ):
    def __init__(self, name, other):
        self.other = float(other)
        super(Adder, self).__init__(name)
        
    
    def handle(self):
        self.output = self.input + self.other
        self.output_changed.emit()
            
##
# Compares two signals with each other
class Comparator( Component ):
    def __init__(self, name, other, op):
        self.other = float(other)
        self.operator = op
        super(Comparator, self).__init__(name)

    
    def handle(self):
        self.output = self.operator(self.input, self.other)
        self.output_changed.emit()
        
        
class Sum( Component ):        
    def __init__(self, name):
        super(Sum, self).__init__(name)
        
    def handle(self):
        #print str(self.input)
        self.output = sum(self.input)
        self.output_changed.emit()

class Div( Component ):        
    def __init__(self, name, other):
        self.other = float(other)
        super(Div, self).__init__(name)
        
    def handle(self):
        self.output = self.input / self.other
        self.output_changed.emit()

class Buffer( Component ):        
    def __init__(self, name, bufSize):
        super(Buffer, self).__init__(name)
        self.bufSize = bufSize
        self.input = []

    def signals_ready(self):
        return len(self.input) == self.bufSize 
                           
    def set_input(self, val):
        print self.name + ".set_input( " + str(val) + " )"
        self.input.insert( 0,val )
        if len(self.input) > self.bufSize:
            self.input.pop()
                
        if self.signals_ready():
            self.handle()
            self._propagate()
        
    def handle(self):
        self.output = self.input
        self.output_changed.emit()

class Avg( Component ):
    def handle(self):
        self.output = sum(self.input) / len(self.input)
                
class Filt( Component ):
    def __init__(self, name, filt_cond):
        super(Filt, self).__init__(name)
        self.filt_cond = filt_cond
        
    def handle(self):
        self.output = filter(lambda input: eval(self.filt_cond), self.input)
        self.output_changed.emit()
                
        
class Sorter( Component ):
    def __init__(self, name, sort_by=None, ordering=None):
        super(Sorter,self).__init__(name)
        self.sort_by = sort_by
        self.reverse = ordering=='DESC'
        
    def handle(self):
        if self.sort_by == None:
            self.input.sort()
            self.output = self.input
        else:
            self.output = input.sort(key=operator.itemgetter(self.sort_by))
        
        if self.reverse: self.output.reverse()

        self.output_changed.emit()

class AnyGate( Component ):
    def __init__(self, name):
        super(AnyGate,self).__init__(name)
        
    def handle(self):
        print type(self.input), self.input
        self.output = not( self.input == [] or self.input == '')
        self.output_changed.emit()
            
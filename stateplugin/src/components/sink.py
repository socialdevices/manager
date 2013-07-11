###
# Implements the Sink functionality (state value and manager connection)
##
from base import Component


from clients import KurreClient

class SimpleStateSink( Component ):
    def __init__(self, name, interface, method):
        super(SimpleStateSink, self).__init__(name)
        self.interface = interface
        self.method = method
        self.changed= False
        
    def setEventMethod_callback(self, cb):
        self.cb = cb
        
    def set_input(self, val):
        self.changed = val != self.input
        super(SimpleStateSink, self).set_input(val)
        
    def signals_ready(self):
        return self.changed
        
    def handle(self):
        self.cb( interface=self.interface, method=self.method, value=self.input )

class StateSink( Component ):
    def __init__(self, name, interface, method):
        super(StateSink, self).__init__(name)
        self.interface = interface
        self.method = method
        self.changed= False
        
    def setEventMethod_callback(self, cb):
        self.cb = cb
        
    def set_input(self, val):
        self.changed = val != self.input
        super(SimpleStateSink, self).set_input(val)
        
    def signals_ready(self):
        return self.changed
        
    def handle(self):
        self.cb( interface=self.interface, method=self.method, value=self.input )


class Printer( Component ):        
    def __init__(self, name):
        super(Printer, self).__init__(name)
        
    def handle(self):
        print str(self.input)
        self.output = self.input
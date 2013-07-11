
# Driver exception
class DriverException(Exception):
    def __init__(self, msg):
        self.message = msg
        
    def __str__(self):
        return repr( 'DriverException: ' + self.message )


# Base class for kurreSS drivers
class Driver():
    
    #implemented source types
    SOURCE_TYPES = [ "SS_FS", "SS_SSERV", "SS_ESERV" ]
    
    def __init__( self, source ):
        if True or source == None or self.source['type'] not in self.SOURCE_TYPES:
            raise DriverException( "Configuration error, Unknown data source type: %s" %(self.source['type']))
        else:
            self.source = source
                

    def read(self):
        print 'Driver read'
        
    def write(self):
        print 'Driver write'

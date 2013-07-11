import threading

class DeviceHandler():
    def __init__(self):
        self.devices = []
        self.deviceLock = threading.Lock()


    def addDevice( self, device ):
        for item in self.devices:
            if item.id == device.id:
                print( "device ", device.id, " already registered" )
                return 0

        self.devices.append( device )
        print( "device appended, devices: ", self.devices )
        return device

    def getDevice( self, devId ):
        for item in self.devices:
            if item.id == devId:
                return item
        return 0

    def clearGroups(self):
        for device in self.devices:
            device.groupId = -1
            device.visited = False

    def clearVisited(self):
        for device in self.devices:
            device.visited = False
    
    def flush(self):
        self.devices = []
    
class Device():
    def __init__(self, devId, neighbours ):
        self.id = devId
        self.neighbours = neighbours
        self.groupId = -1
        self.visited = False
        
    def setNeighbours( self, neighbours ):
        self.neighbours = neighbours

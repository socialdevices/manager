from device import *
from proximity import ProximityManager
import SocketServer
import argparse
import os
import socket
import sys
from profiler.decorators import profile

# Echo server program

#from db import *

class MyServer(SocketServer.ThreadingTCPServer):
    def __init__(self, server_address, RequestHandlerClass,dbAddr):
        SocketServer.ThreadingTCPServer.__init__(self,server_address,RequestHandlerClass)
        self.deviceHandler = DeviceHandler()
        #self.dataBase = DbConn(dbAddr)
        self.proximityManager = ProximityManager( self.deviceHandler )

@profile
class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client

        self.data = self.request.recv(1024).strip()
        if not self.data:
            return
        
        #print("{} wrote:".format(self.client_address[0]))         
        print(self.data)

        reply = self.parse(self.data)

        print "replying", reply
        self.request.send(reply)


    def parse( self, data ):
        msg = data.replace(" ", "").split( "," )
        print msg
        cmd = msg.pop(0)
            
        if cmd == "set_group":
            dev_id = msg.pop(0)
            device = self.server.deviceHandler.getDevice( dev_id )
            print "device", dev_id, "updating its prox info, neighbours:", msg
            if not device:
                print "device not found! creating a new one with neighbours", msg
                self.server.deviceHandler.addDevice( Device( dev_id, msg ) )
            else:
                device.setNeighbours( msg )
            self.server.proximityManager.update( device )
            return "ok"

        elif cmd == "get_group":
            dev_id = msg.pop(0)
            device = self.server.deviceHandler.getDevice( dev_id )
            print "getting device", dev_id, "proximity group"

            if not device:
                device = self.server.deviceHandler.addDevice( Device( dev_id, [] ) )
                self.server.proximityManager.addDevice( device )
                
            group = self.server.proximityManager.get_group( device )
            group.remove(device)
            return ("[]", ",".join( [item.id for item in group ] ))[len(group) != 0]

        elif cmd == "add_device":
            dev_id = msg.pop(0)
            ret = self.server.deviceHandler.addDevice( Device(dev_id, []) )
            if ret == 0:
                return "already exists"
            else:
                self.server.proximityManager.addDevice( ret )
                return "ok"

        
        elif cmd == "flush":
            print "flush"
            self.server.deviceHandler.flush()
            self.server.proximityManager.flush()
            return "ok"
        
        elif cmd == "shutdown":
            return "quitter"
        
        else:
            return "Unrecognized command!"



if __name__ == "__main__":
    if not sys.path.count(os.getcwd()):
        sys.path.append(os.getcwd())
    
    parser = argparse.ArgumentParser(description='A server that stores proximity device information.')
    parser.add_argument('-p', '--port', default=50007, type=int, dest='port', help='server port (default 50007)')
    args = parser.parse_args()
    
    HOST = "localhost"
    
    try:
        # Create the server
        server = MyServer((HOST, args.port), MyTCPHandler, "localhost")
        sys.stdout.write('Proximity server is running at %s:%s\n' % (HOST, args.port))
        sys.stdout.write('Quit the server with CONTROL-C.\n')
        
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
    except socket.error, e:
        sys.stderr.write('Error: %s\n' % e.args[1])
        sys.exit(1)
    except KeyboardInterrupt:
        sys.stdout.write('\nProximity server shutted down.\n')
        sys.exit(0)

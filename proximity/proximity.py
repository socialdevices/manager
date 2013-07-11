import networkx as nx

class ProximityManager():
    def __init__(self, deviceManager):
        self.groups = []
        self.deviceManager = deviceManager
        self.visited = []
        self.gid = 0

        self.proxNet = nx.Graph()


    def get_group(self, device ):
        return nx.node_connected_component( self.proxNet, device )


    def update(self, dev = 0 ):
        if not dev:
            return
        else:
            print dev, dev.neighbours, nx.edges( self.proxNet, dev )
            print self.proxNet.nodes(), self.proxNet.edges()
            self.proxNet.remove_edges_from( nx.edges( self.proxNet, dev ) )

            registered = []
            for item in dev.neighbours:
                neighbour = self.deviceManager.getDevice( item )
                if neighbour != 0:
                    registered.append( neighbour )
                    
            self.proxNet.add_edges_from( [(dev, item) for item in registered] )

    def addDevice( self, device ):
        self.proxNet.add_node( device )
        self.update( device )

    def flush( self ):
        self.proxNet.clear()

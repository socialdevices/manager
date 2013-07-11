import httplib, json, requests

class Connection:

    def __init__( self, host, port, api_version ):
        self.host = host
        self.port = port
        self.api_version = api_version
        self.printer = None

    def api_get( self, path ):
        try:
            addr = 'http://' + self.host + ':' + self.port + path + '?format=json'    
            r = requests.get( addr )
            return json.loads( r.content )
        except Exception, e:
            print e
            return None
        
    def api_update( self, arg ):
        api=[]
        try:    
            # get state methods
            path = '/api/' + self.api_version + '/' + 'devices/' + arg
            dev = self.api_get( path )
            interfaces = self.api_get( dev['interfacesUri'] ) 

            for iface in interfaces['objects']:
                iface_descr = {'methods':[]}
                iface_inst = self.api_get( iface['interface'] )

                #print 'iface_inst from interface: {0}'.format(iface_inst)

                iface_descr[iface_inst['name']] = iface_inst['id']

                # get the methods structure
                methods = self.api_get( iface_inst['methodsUri'] )
                
                #print 'methods from methodsUri: {0}'.format(methods)

                for method in methods['objects']:
                    method_inst = self.api_get( method['method'] )
                    iface_descr['methods'].append( {method_inst['name']: method_inst['id'],
                                                    'parameters': method_inst['parameters']} )

                api.append( iface_descr )            

            return api

        except Exception, e:
            print e
            return None


    def set_printer( self, printer ):
        self.printer = printer

    def post( self, path, data=None ):
        #print "in post", self.host, path,":", self.port, data

        resp = ""
        try:			
            con = httplib.HTTPConnection( self.host, self.port, timeout = 10 )
            #con.set_debuglevel(10)
            #headers = { 'Content-Type': 'application/json' }

            body = json.dumps( data )				
            con.putrequest('POST', path)
            con.putheader('content-type', 'application/json')
            con.putheader('content-length', str(len(body)))
            con.endheaders()
            con.send(body)
            resp = con.getresponse()
            
            #print resp.read()
            
            if resp.status < 200 or resp.status > 204:
                print resp.read()
                #self.printer.write( resp.read() )

            return resp.status			
    
        except Exception, e:
            return e
            #return eno

        return resp.status

    def put( self, path, data=None ):
        #print "in put", self.host, path,":", self.port, data

        resp = ""
        try:
            con = httplib.HTTPConnection( self.host, self.port, timeout = 10 )
            #con.set_debuglevel(10)

            body = json.dumps( data )				
            con.putrequest('PATCH', path)
            con.putheader('content-type', 'application/json')
            con.putheader('content-length', str(len(body)))
            con.endheaders()
            con.send(body)
            resp = con.getresponse()

            if resp.status < 200 or resp.status > 204:
                print resp.read()
                #self.printer.write( resp.read() )

            return resp.status			


        except Exception, e:
            return e

        return resp.status

    def patch( self, path, data=None ):
        print "in patch", self.host, ":", self.port, path, data

        resp = ""
        try:
            con = httplib.HTTPConnection( self.host, self.port, timeout = 10 )
            #con.set_debuglevel(10)

            body = json.dumps( data )				
            con.putrequest('PATCH', path)
            con.putheader('content-type', 'application/json')
            con.putheader('content-length', str(len(body)))
            con.endheaders()
            con.send(body)
            resp = con.getresponse()

            if resp.status < 200 or resp.status > 204:
                print resp.read()
                #self.printer.write( resp.read() )

            return resp.status			


        except Exception, e:
            return e

        return resp.status

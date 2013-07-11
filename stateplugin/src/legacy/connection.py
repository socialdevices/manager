import httplib, simplejson

class Connection:

	def __init__( self, host, port ):
		self.host = host
		self.port = port
		#self.api_version = api_version
		self.printer = None


	def set_printer( self, printer ):
		self.printer = printer

	def post( self, path, data=None ):
		#print "in post", self.host, path,":", self.port, data

		resp = ""
		try:			
			con = httplib.HTTPConnection( self.host, self.port, timeout = 10 )
#			con.set_debuglevel(10)
			#headers = { 'Content-Type': 'application/json' }
			
			body = simplejson.dumps( data )				
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
#			#return eno

		return resp.status

	def put( self, path, data=None ):
		#print "in put", self.host, path,":", self.port, data
			
		resp = ""
		try:
			con = httplib.HTTPConnection( self.host, self.port, timeout = 10 )
			#con.set_debuglevel(10)
	
			body = simplejson.dumps( data )				
			con.putrequest('PUT', path)
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

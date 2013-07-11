import MySQLdb, sys
import time

class DbConn():
    def __init__(self, dbfile):
        self.i=0
        try:
            self.database = MySQLdb.connect(dbfile,"root","","kurre")
            self.db = self.database.cursor()
        except:
            print "Error connecting to database"
		
        


    def add_device(self, dev):


        
        try:
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            selfMac = long(dev.id.replace( ":", "" ),16)
            print dev.id, selfMac, now
            print self.db.execute("""INSERT INTO devices (name, mac_address, created)
                                  VALUES ( "%s", "%s", "%s" )""",
                                  (dev.id, selfMac, now ) )

            print self.db.execute( """SELECT * FROM devices""" )
            print self.db.fetchall()
            self.database.commit()
	
        except:
            print sys.exc_info()
            return "error"
	
        return "ok"

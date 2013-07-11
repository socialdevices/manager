from base import SourceComp
import subprocess

###
 # implements a source component, which on tick() call reads tracker database field according to params given
 # signal out: a list of dicts of database rows found with the term "field"
 # source allows passing custom queries to the
 ##
class TrackerSource( SourceComp ):
    def __init__( self, name, q_entity, fields=None ):
        super(TrackerSource, self).__init__(name)
        self.q_entity = q_entity
        self.fields = fields
        
        #self.query = self._create_query()
             
    def _create_query(self, q_entity, field):
        otype = q_entity.split(':')[0]
        if field == None:
            print "Must select field(s) to include in query"
            #q = "select * { ?x a " + self.q_entity + "; }"            
        elif type(field) == str: #single field
            #date is a special case (need to dig deeper for unpacked value
            if field == 'dtstart':
                q = "select ?" + field + " { ?x a " + q_entity + "; " + otype + ":" + field + " ?s . ?s ncal:dateTime ?" +field+ " }"
            else:
                q = "select ?" + field + " { ?x a " + q_entity + "; " + otype + ":" + field + " ?" + field + " }"
        elif type(field) == list:
            varis = []
            terms =[]
            for field in self.fields:
                varis.append('?' + field)
                if field == 'dtstart':
                    terms.append(otype + ":" + field + " ?s . ?s ncal:dateTime ?" + field)    
                else:
                    terms.append(otype + ":" + field + " ?" + field)    
                    
            q='select ' + ' '.join(varis) + " { ?x a " + self.q_entity + "; " + '; '.join(terms) +' }'
            
        return q

    def read(self):
        inp = []
        # get the query one term at a time.. 
        if type( self.fields ) == str:
                p=subprocess.Popen( ['/usr/bin/tracker-sparql', '-q', self._create_query( self.q_entity, self.fields)], stdout=subprocess.PIPE )
                qres = [x.strip() for x in p.communicate()[0].replace('Results:','').split('\n')]
            
                return filter(None, qres)

        elif type( self.fields ) == list:
            for field in self.fields:
                p=subprocess.Popen( ['/usr/bin/tracker-sparql', '-q', self._create_query( self.q_entity, field)], stdout=subprocess.PIPE )
                qres = [x.strip() for x in p.communicate()[0].replace('Results:','').split('\n')]
                
                inp.append( filter( None, qres) )
            
        # transpose the result..
            return zip(*inp)



class DBusSource( SourceComp ):
    def __init__(self, name, source):
        super(DBusSource, self).__init__(name, source)
        
class UiSource( SourceComp ):
    def __init__(self, name, uiComp):
        super( UiSource, self ).__init__(name)
        self.uiComp = uiComp
        
        if not self.uiComp: 
            print "Warning, ui component not supplied. I will not work!"

    # requires a getVal method..
    def read(self):
        if self.uiComp:
            return self.uiComp.getState()



        
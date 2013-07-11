from base import SourceComp

###
 # implements a source component, which on tick() call reads tracker database field according to params given
 # signal out: a list of dicts of database rows found with the term "field"
 # source allows passing custom queries to the
 ##
class TrackerSource( SourceComp ):
    def __init__( self, name, source, q_entity, fields ):
        super(TrackerSource, self).__init__(name, source)
        self.q_entity = q_entity
        self.fields = fields


        self.query = self._create_query()
        
        if self.source == None:
            print "Error, source Component _must_ be selected, this component will not work!"

        print self.source
        
    
    def _create_query(self):
        otype = self.q_entity.split(':')[0]
        if type(self.fields) == str: #single field
            q = "select distinct ?" + self.fields + " { ?x a " + self.q_entity + "; " + otype + ":" + self.fields + " ?" + self.fields + ";}"
        elif type(self.fields) == list:
            varis = []
            terms =[]
            for field in self.fields:
                varis.append('?' + field)
                terms.append(otype + ":" + field + ' ?' + field)
                

            q='select distinct ' + ' '.join(varis) + " { ?x a " + self.q_entity + "; " + '; '.join(terms) +';}'
            
        return q

class DBusSource( SourceComp ):
    def __init__(self, name, iface, path, method):
        super(DBusSource, self).__init__(name, source)
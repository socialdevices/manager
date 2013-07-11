import time, re, platform
from datetime import datetime

from decorators import *

class CalendarSource(object):
    def __init__(self):
        pass

    @classmethod
    @precondition
    def eventApproaching(self, params):
        source = { 'TrackerSource': {'name':'Calendar', 'q_entity': 'ncal:Event', 'fields': ['uid','dtstart']} }
        filter_c = { 'Filt': {'name':'Closest upcoming', 'filt_cond': 'datetime.strptime( input[1], \"%Y-%m-%dT%H:%M:%SZ\") >= datetime.utcnow()'} }
        sink = { 'SimpleStateSink': {'name':'CalEvent State', 'interface':'CalendarSource', 'method':'eventApproaching'} }

        # the return structure defines the connection of components..
        return [source, filter_c, sink]

        try:
            return True
        except:
            return False
    
    @classmethod
    @body
    def getCalendarEvent(self, params):
        try:
            eid = str(params.get("eid",""))
            event = { "type": "deviceInterfaces.calendarSource.CalendarEvent", "init_parameters" : {"eid" : "", "time": 0, "subject": "Not-Found", "location": ""} }
            
            p = re.compile("arm")
            if p.match(platform.machine()):
                
                import sqlite3
                try:
                        connection = sqlite3.connect('/home/user/.calendar/db')
                except:
                        print "Error connecting to database"
                        return "nothing"

                c = connection.cursor()

                issue = open('/etc/issue').read().strip().lower()
                sql = None
                if issue.startswith('maemo'):
                    # N900
                    sql = "select Components.ComponentId, Components.Summary, Components.Location, Components.Description, Components.DateStart, Components.DateEnd  from Components where Id='"+eid+"'"
                else:
                    # MeeGo
                    sql = "select Components.ComponentId, Components.Summary, Components.Location, Components.Description, Components.DateStart, Components.DateEndDue  from Components where ComponentId='"+eid+"'"
                
                c.execute(sql)    
                
                location = ""
                begin_time = 0
                end_time = 0 
                subject = ""
                for row in c:
                        #print row
                        location = row[2]
                        begin_time = row[4]
                        end_time = row[5]
                        subject = row[1]
               
                if not subject:
                    event = { "type": "deviceInterfaces.calendarSource.CalendarEvent", "init_parameters" : {"eid" : eid, "time": 0, "subject": "Not-Found", "location": ""} }
                else:
                    event = { "type": "deviceInterfaces.calendarSource.CalendarEvent", "init_parameters" : {"eid" : eid, "time": begin_time, "subject": subject, "location": location} }
            
            else:
                eid = params.get("eid","")
            
                # Notice! time must be epoch time!!!
                event = { "type": "deviceInterfaces.calendarSource.CalendarEvent", "init_parameters" : {"eid" : eid, "time": time.time(), "subject": "Social devices meeting", "location": "Tampere"} }         
            
            print "Event: "+str(event)
            return event
            
        except Exception, eex:
            print str(eex)
            return None
    








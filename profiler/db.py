from datetime import datetime
import os
import sqlite3

class ProfilerDatabase(object):
    
    def __init__(self):
        db_path = os.path.join(os.path.dirname(__file__), 'profiler.sqlite')
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_database()
    
    def __del__(self):
        self.conn.close()
    
    def _create_database(self):
        c = self.conn.cursor()
        
        
        # Create profiler group runs table
        c.execute('''CREATE TABLE IF NOT EXISTS "profiler_group_runs" ( 
                         "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL, 
                         "name" VARCHAR NOT NULL, 
                         "x_label" VARCHAR, 
                         "num_profiler_runs" INTEGER NOT NULL, 
                         "first" INTEGER NOT NULL, 
                         "last" INTEGER NOT NULL, 
                         "increment" INTEGER NOT NULL, 
                         "started" DATETIME NOT NULL, 
                         "ended" DATETIME
                     )''')
        
        # Create profiler runs table
        c.execute('''CREATE TABLE IF NOT EXISTS "profiler_runs" ( 
                         "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL, 
                         "group_id" INTEGER NOT NULL, 
                         "started" DATETIME NOT NULL, 
                         "ended" DATETIME, 
                         FOREIGN KEY ("group_id") REFERENCES "profiler_group_runs" ("id"), 
                         UNIQUE ("id", "group_id") 
                     )''')
        
        # Create requests table
        c.execute('''CREATE TABLE IF NOT EXISTS "requests" ( 
                         "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL, 
                         "profiler_run_id" INTEGER NOT NULL, 
                         "request_num" INTEGER NOT NULL, 
                         "cum_function_calls" INTEGER, 
                         "cum_primitive_calls" INTEGER, 
                         "cum_time" NUMERIC, 
                         "status_code" INTEGER, 
                         "started" DATETIME NOT NULL, 
                         "ended" DATETIME, 
                         FOREIGN KEY ("profiler_run_id") REFERENCES "profiler_runs" ("id"), 
                         UNIQUE ("profiler_run_id", "request_num") 
                     )''')
        
        # Create functions table
        c.execute('''CREATE TABLE IF NOT EXISTS "functions" ( 
                         "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL,
                         "group_id" INTEGER NOT NULL, 
                         "module" VARCHAR NOT NULL, 
                         "name" VARCHAR NOT NULL, 
                         "line" INTEGER NOT NULL, 
                         "created" DATETIME NOT NULL, 
                         FOREIGN KEY ("group_id") REFERENCES "profiler_group_runs" ("id"), 
                         UNIQUE ("group_id", "module", "name", "line") 
                     )''')
        
        # Create the stats table
        c.execute('''CREATE TABLE IF NOT EXISTS "stats" ( 
                         "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL, 
                         "request_id" INTEGER NOT NULL, 
                         "function_id" INTEGER NOT NULL, 
                         "ncalls" VARCHAR NOT NULL, 
                         "actual_calls" INTEGER NOT NULL, 
                         "primitive_calls" INTEGER, 
                         "tottime" NUMERIC NOT NULL, 
                         "tottime_percall" NUMERIC NOT NULL, 
                         "cumtime" NUMERIC NOT NULL, 
                         "cumtime_percall" NUMERIC NOT NULL, 
                         "created" DATETIME NOT NULL, 
                         FOREIGN KEY ("request_id") REFERENCES "requests" ("id"), 
                         FOREIGN KEY ("function_id") REFERENCES "functions" ("id"), 
                         UNIQUE ("request_id", "function_id") 
                     )''')
         
        self.conn.commit()
        c.close()
    
    def start_profiler_group_run(self, name, num_profiler_runs, first, last, increment, started=None):
        c = self.conn.cursor()
        
        if started is None:
            date = datetime.now()
            started = date.strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute('''INSERT INTO "profiler_group_runs" 
                     ("name", "num_profiler_runs", "first", "last", "increment", "started")
                     VALUES (:name, :num_profiler_runs, :first, :last, :increment, :started)
        ''', {"name": name, "num_profiler_runs": num_profiler_runs, "first": first, "last": last, "increment": increment, "started": started})
        
        self.conn.commit()
        c.close()
        
        return c.lastrowid
    
    def stop_profiler_group_run(self, group_id, ended=None):
        c = self.conn.cursor()
        
        if ended is None:
            date = datetime.now()
            ended = date.strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute('''UPDATE "profiler_group_runs" 
                     SET "ended" = :ended 
                     WHERE "id" = :id
        ''', {"ended": ended, "id": group_id})
        
        self.conn.commit()
        c.close()
     
    def start_profiler_run(self, group_id, started=None):
        c = self.conn.cursor()
        
        if started is None:
            date = datetime.now()
            started = date.strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute('''INSERT INTO "profiler_runs" 
                     ("group_id", "started") 
                     VALUES (:group_id, :started)
        ''', {"group_id": group_id, "started": started})
        
        self.conn.commit()
        c.close()
        
        return c.lastrowid
    
    def stop_profiler_run(self, profiler_run_id, ended=None):
        c = self.conn.cursor()
        
        if ended is None:
            date = datetime.now()
            ended = date.strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute('''UPDATE "profiler_runs" 
                     SET "ended" = :ended 
                     WHERE "id" = :id
        ''', {"ended": ended, "id": profiler_run_id})
        
        self.conn.commit()
        c.close()
    
    def start_request(self, profiler_run_id, request_num, started=None):
        c = self.conn.cursor()
        
        if started is None:
            date = datetime.now()
            started = date.strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute('''INSERT INTO "requests" 
                     ("profiler_run_id", "request_num", "started")
                     VALUES (:profiler_run_id, :request_num, :started)
        ''', {"profiler_run_id": profiler_run_id, "request_num": request_num, "started": started})
        
        self.conn.commit()
        c.close()
        
        return c.lastrowid
    
    def stop_request(self, request_id, status_code, ended=None):
        c = self.conn.cursor()
        
        if ended is None:
            date = datetime.now()
            ended = date.strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute('''UPDATE "requests" 
                     SET "status_code" = :status_code, "ended" = :ended 
                     WHERE "id" = :id
        ''', {"status_code": status_code, "ended": ended, "id": request_id})
        
        self.conn.commit()
        c.close()
    
    def update_request_stats(self, request_id, function_calls, primitive_calls, time):
        c = self.conn.cursor()
        
        c.execute('''UPDATE "requests" 
                     SET "cum_function_calls" = :function_calls, "cum_primitive_calls" = :primitive_calls, "cum_time" = :time 
                     WHERE "id" = :id
        ''', {"function_calls": function_calls, "primitive_calls": primitive_calls, "time": time, "id": request_id})
        
        self.conn.commit()
        c.close()
    
    def get_function_id(self, group_id, module, name, line):
        c = self.conn.cursor()
        
        c.execute('''SELECT "id" 
                     FROM "functions" 
                     WHERE "group_id" = :group_id AND "module" = :module AND "name" = :name AND "line" = :line 
                     LIMIT 1
        ''', {"group_id": group_id, "module": module, "name": name, "line": line})
        
        data = c.fetchone()
        
        if data is None:
            return None
        else:
            return data[0]
    
    def add_function(self, group_id, module, name, line, created=None):
        c = self.conn.cursor()
        
        if created is None:
            date = datetime.now()
            created = date.strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute('''INSERT INTO "functions" 
                     ("group_id", "module", "name", "line", "created")
                     VALUES (:group_id, :module, :name, :line, :created)
        ''', {"group_id": group_id, "module": module, "name": name, "line": line, "created": created})
        
        self.conn.commit()
        c.close()
        
        return c.lastrowid
    
    def add_stats(self, request_id, function_id, ncalls, actual_calls, primitive_calls, tottime, tottime_percall, cumtime, cumtime_percall, created=None):
        c = self.conn.cursor()
        
        if created is None:
            date = datetime.now()
            created = date.strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute('''INSERT INTO "stats" 
                     ("request_id", "function_id", "ncalls", "actual_calls", "primitive_calls", "tottime", "tottime_percall", "cumtime", "cumtime_percall", "created")
                     VALUES (:request_id, :function_id, :ncalls, :actual_calls, :primitive_calls, :tottime, :tottime_percall, :cumtime, :cumtime_percall, :created)
        ''', {"request_id": request_id, "function_id": function_id, "ncalls": ncalls, "actual_calls": actual_calls, "primitive_calls": primitive_calls, "tottime": tottime, "tottime_percall": tottime_percall, "cumtime": cumtime, "cumtime_percall": cumtime_percall, "created": created})
        
        self.conn.commit()
        c.close()
        
        return c.lastrowid
    
    def get_functions(self, group_id):
        c = self.conn.cursor()
        
        c.execute('''SELECT "id", "module", "name", "line" 
                     FROM "functions" 
                     WHERE "group_id" = :group_id 
        ''', {"group_id": group_id})
        
        data = c.fetchall()
        
        return data
    
    def get_requests(self, profiler_run_id):
        c = self.conn.cursor()
        
        c.execute('''SELECT "id" 
                     FROM "requests" 
                     WHERE "profiler_run_id" = :profiler_run_id 
                     ORDER BY "request_num"
        ''', {"profiler_run_id": profiler_run_id})
        
        data = c.fetchall()
        
        return data
    
    def get_function_stats(self, function_id):
        c = self.conn.cursor()
        
        c.execute('''SELECT r."profiler_run_id", r."request_num", ROUND(AVG(s."actual_calls"), 3) AS actual_calls, ROUND(AVG(s."tottime"), 3) AS tottime, ROUND(AVG(s."cumtime"), 3) AS cumtime 
                     FROM "stats" s 
                     INNER JOIN "requests" r ON r.id = s.request_id 
                     WHERE s."function_id" = :function_id 
                     GROUP BY r."request_num" 
                     ORDER BY r."request_num" 
        ''', {"function_id": function_id})
        
        data = c.fetchall()
        
        return data
    
    def get_profiler_group_runs(self):
        c = self.conn.cursor()
        
        c.execute('''SELECT "id", "name", "started", "ended" 
                     FROM "profiler_group_runs" 
                     ORDER BY "id"''')
        
        data = c.fetchall()
        
        return data
    
    def get_profiler_group_run(self, group_id):
        c = self.conn.cursor()
        
        c.execute('''SELECT "id", "name", "x_label", "num_profiler_runs", "first", "last", "increment", "started", "ended" 
                     FROM "profiler_group_runs" 
                     WHERE "id" = :id 
                     LIMIT 1
        ''', {"id": group_id})
        
        data = c.fetchone()
        
        if data is None:
            return None
        else:
            return data
    
    def update_profiler_group_run_x_label(self, group_id, x_label):
        c = self.conn.cursor()
        
        c.execute('''UPDATE "profiler_group_runs" 
                     SET "x_label" = :x_label 
                     WHERE "id" = :id
        ''', {"x_label": x_label, "id": group_id})
        
        self.conn.commit()
        c.close()
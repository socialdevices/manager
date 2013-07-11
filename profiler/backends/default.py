from datetime import datetime
from django.conf import settings
from profiler.db import ProfilerDatabase
import cStringIO
import glob
import inspect
import logging
import os
import pstats
import re
import requests
import time

logger = logging.getLogger(__name__)

class DefaultProfiler(object):
    
    def __init__(self, num_runs, first, num_requests, increment, condition):
        self.db = ProfilerDatabase()
        self.num_runs = num_runs
        self.first = first
        self.num_requests = num_requests
        self.increment = increment
        self.condition = condition
        self.protocol = settings.PROFILER.get('MY_SITE_PROTOCOL', 'http')
        self.host = settings.PROFILER.get('MY_SITE_HOST', 'localhost')
        self.port = settings.PROFILER.get('MY_SITE_PORT', '')
        self.base_url = '%s://%s' % (self.protocol, self.host)
        if self.port:
            self.base_url += ':%s' % self.port
        self.log_dir = settings.PROFILER.get('LOG_DIR', 'profiling_logs')
        self.project_root = getattr(settings, 'PROJECT_ROOT')
        
        self.profiler_tests = []
        self.profiler_teardown_methods = {}
        backend_methods = inspect.getmembers(self, inspect.ismethod)
        for method in backend_methods:
            if method[0].startswith('profile_'):
                self.profiler_tests.append(method)
            if method[0].startswith('teardown_'):
                self.profiler_teardown_methods[method[0]] = method
        self.previous_values = {}
        
    
    def start_profiling(self, test_index):
        profiler_test = self.profiler_tests[test_index]
        
        profiler_group_run_name = profiler_test[0].replace('profile_', '')
        profiler_group_run_id = self.db.start_profiler_group_run(profiler_group_run_name, self.num_runs, self.first, self.num_requests, self.increment)
        
        # Repoze profiler does not profile the first request
        if self._first_request():
            # After server restart, the python interpreter does some initialization
            logger.debug('Starting initialization call')
            successful = profiler_test[1](1)
            if successful:
                logger.debug('Initialization call was successful')
            
            logger.debug('Starting initialization call teardown')
            try:
                teardown_method_name = 'teardown_%s' % profiler_group_run_name
                self.profiler_teardown_methods[teardown_method_name][1](1)
            except KeyError:
                logger.error('No teardown method named %s' % teardown_method_name)
            logger.debug('Initialization call teardown finished')
            
            
            for i in range(self.num_runs):
                #self._reset_profilers()
                logger.debug('Started profiler run %i' % (i + 1))
                profiler_run_id = self.db.start_profiler_run(profiler_group_run_id)
                
                num_ok = 0
                for j in range(1, self.num_requests + 1):
                    self._reset_profilers()
                    logger.debug('Starting profiling call %i' % j)
                    
                    if j >= self.first and (j % self.increment) == 0:
                        request_id = self.db.start_request(profiler_run_id, j)
                    successful = profiler_test[1](j)
                    
                    if successful:
                        num_ok += 1
                        logger.debug('Profiling call %i was successful' % j)
                    
                    date = datetime.now()
                    ended = date.strftime('%Y-%m-%d %H:%M:%S')
                    
                    if j >= self.first and (j % self.increment) == 0:
                        self.db.stop_request(request_id, successful, ended=ended)
                        self._save_stats(profiler_group_run_id, request_id)
                    else:
                        with self.condition:
                            while True:
                                lock_files = glob.glob(os.path.join(self.log_dir, '*.lock'))
                                if len(lock_files) == 0:
                                    break
                                self.condition.wait()
                logger.debug('%i/%i profiling calls finished successfully' % (num_ok, self.num_requests))
                
                logger.debug('Starting teardown')
                try:
                    teardown_method_name = 'teardown_%s' % profiler_group_run_name
                    self.profiler_teardown_methods[teardown_method_name][1](self.num_requests)
                except KeyError:
                    logger.error('No teardown method named %s' % teardown_method_name)
                logger.debug('Teardown finished')
                
                self.db.stop_profiler_run(profiler_run_id)
                logger.debug('Ended profiler run %i' % (i + 1))
            #self._add_devices(profiler_run_id, self.num_requests)
            #self._add_devices_and_interfaces(profiler_run_id, self.num_requests)
        else:
            logger.error('Error in first request')
        
        self.db.stop_profiler_group_run(profiler_group_run_id)
    
    def get_tests(self):
        tests = []
        for test in self.profiler_tests:
            tests.append(test[0].replace('profile_', ''))
        return tests
    
    def _first_request(self):
        pass
    
    def _start_request(self, profiler_run_id, request_num):
        request_id = self.db.start_request(profiler_run_id, request_num)
        
        return request_id
    
    def _reset_profilers(self):
        # Reset the repoze.profiler
        path = '/__profile__'
        url = self.base_url + path
        payload = {'clear': 'Clear'}
        response = requests.post(url, data=payload)
        
        if response.status_code != 200:
            logger.error('Resetting repoze.profiler failed')
        else:
            logger.debug('Repoze.profiler resetted')
        
        # Reset the profiler decorators
        for filename in os.listdir(self.log_dir):
            if filename.endswith('.prof'):
                file_path = os.path.join(self.log_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception, e:
                    logger.error('Could not reset profile decorators')
        logger.debug('Profile decorators resetted')
        logger.debug('Profiler resetted')
        
    def _save_stats(self, group_id, request_id):
        with self.condition:
            while True:
                lock_files = glob.glob(os.path.join(self.log_dir, '*.lock'))
                if len(lock_files) == 0:
                    break
                self.condition.wait()
        
        logger.debug('Processing stats')
        
        stats_files = glob.glob(os.path.join(self.log_dir, '*.prof'))
        
        if len(stats_files) > 0:
            first_file = stats_files.pop(0)
            stream = cStringIO.StringIO()
            stats = pstats.Stats(first_file, stream=stream)
            
            for stats_file in stats_files:
                stats.add(stats_file)
            
            # Restrict the stats only to the files in the kurre project dir
            stats.print_stats(self.project_root)
            
            stream.seek(0)
            # Read the stream, line by line
            for line in stream:
                m = re.search('^\s+(?P<function_calls>[0-9]+) function calls(?: \((?P<primitive_calls>[0-9]+) primitive calls\))? in (?P<time>[0-9]+\.[0-9]+) CPU seconds', line, re.IGNORECASE)
                if m:
                    function_calls = m.group('function_calls')
                    primitive_calls = m.group('primitive_calls')
                    time = m.group('time')
                    self.db.update_request_stats(request_id, function_calls, primitive_calls, time)
                    #print 'function calls: %s - primitive calls: %s - time: %s' % (m.group('function_calls'), m.group('primitive_calls'), m.group('time'))
                
                
                m = re.search('^\s+(?P<ncalls>(?P<actual_calls>[0-9]+)(?:/(?P<primitive_calls>[0-9]+))?)\s+(?P<tottime>[0-9]+\.[0-9]+)\s+(?P<tottime_percall>[0-9]+\.[0-9]+)\s+(?P<cumtime>[0-9]+\.[0-9]+)\s+(?P<cumtime_percall>[0-9]+\.[0-9]+)\s+(?P<filename>[^:]+):(?P<line>[0-9]+)\((?P<function>[^)]+)\)\n$', line, re.IGNORECASE)
                if m:
                    ncalls = m.group('ncalls')
                    actual_calls = m.group('actual_calls')
                    primitive_calls = m.group('primitive_calls')
                    tottime = m.group('tottime')
                    tottime_percall = m.group('tottime_percall')
                    cumtime = m.group('cumtime')
                    cumtime_percall = m.group('cumtime_percall')
                    filename = m.group('filename')
                    line_num = m.group('line')
                    function = m.group('function')
                    
                    module = filename.replace(self.project_root + os.path.sep, '')
                    
                    function_id = self.db.get_function_id(group_id, module, function, line_num)
                    if not function_id:
                        function_id = self.db.add_function(group_id, module, function, line_num)
                        
                    self.db.add_stats(request_id, function_id, ncalls, actual_calls, primitive_calls, tottime, tottime_percall, cumtime, cumtime_percall)
                    #print 'ncalls: %s - actual_calls: %s - primitive_calls: %s - tottime: %s - tottime_percall: %s - cumtime: %s - cumtime_percall: %s - filename: %s - line: %s - function: %s' % (m.group('ncalls'), m.group('actual_calls'), m.group('primitive_calls'), m.group('tottime'), m.group('tottime_percall'), m.group('cumtime'), m.group('cumtime_percall'), m.group('filename'), m.group('line'), m.group('function'))
            
            logger.debug('Finished processing stats')
            #f = open('test_stats.txt', 'a')
            #f.write(stream.getvalue())
            #f.close()

class ProfilerError(Exception):
    """Base class for profiler errors."""
    pass

class ProfilingCallError(ProfilerError):
    """Used to indicate that a profiling call failed."""
    pass


#def main():
#    parser = argparse.ArgumentParser(description="A profiling utility for testing Kurre's performance")
#    parser.add_argument('-n', '--num', default=100, type=int, dest='num', help='number of devices (default 100)')
#    args = parser.parse_args()
#    
#    wm = pyinotify.WatchManager() # Watch Manager
#    mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY # watched events
#    
#    
#    condition = threading.Condition()
#    notifier = pyinotify.ThreadedNotifier(wm, EventHandler(condition))
#    notifier.start()
#    
#    try:
#        watch_path = settings.PROFILER.get('LOG_DIR', '')
#        wdd = wm.add_watch(watch_path, mask)
#        
#        start_time = time.time()
#        profiler = DefaultProfiler(args.num, condition)
#        profiler.start_profiling()
#        
#    except Exception, e:
#        print str(e)
#    else:
#        elapsed = time.time() - start_time
#        print 'Profiling finished in %i seconds\n' % elapsed
#    finally:
#        wm.rm_watch(wdd.values())
#        notifier.stop()
#        
#        sys.exit(0)
#    
#if __name__ == "__main__":
#    main()

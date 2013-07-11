import cProfile
import os
import threading
from django.conf import settings

class profile(object):
    """
    A decorator that can be used to profile methods or functions. This decorator should only 
    be initialized once for every function. Thus, the function, method or class to be profiled
    must be called once from the main thread. The calls to __call__ can then be done from
    separate threads.
    """
    
    def __init__(self, f):
        self.f = f
        if getattr(settings, 'PROFILING', False):
            #print '__init__ start - %s' % threading.currentThread().getName()
            self.profiler = cProfile.Profile()
            self.lock = threading.Lock()
            self.log_dir = settings.PROFILER.get('LOG_DIR', '')
            #print '__init__ end - %s' % threading.currentThread().getName() 
    
    def __call__(self, *args, **kwargs):
        if getattr(settings, 'PROFILING', False):
            #print '__call__ start - %s' % threading.currentThread().getName()
            # Used to indicate to profiler.py that a thread is in the middle of its work
            try:
                lock_filename = '%s.lock' % threading.currentThread().getName()
                lock_path = os.path.join(self.log_dir, lock_filename)
                lock_file = open(lock_path, 'w')
            finally:
                lock_file.close()
            
            self.lock.acquire()
            try:
                filename =  '%s.prof' % self.f.__name__
                file_path = os.path.join(self.log_dir, filename)
                
                if not os.path.exists(file_path):
                    self.profiler = cProfile.Profile()
                    
                return_value = self.profiler.runcall(self.f, *args, **kwargs)
                self.profiler.dump_stats(file_path)
            finally:
                self.lock.release()
                
                # Used to indicate to kurre_profiler that a thread has done its work
                try:
                    os.remove(lock_path)
                except:
                    pass
            
            #print '__call__ end - %s' % threading.currentThread().getName()
            return return_value
        else:
            return self.f(*args, **kwargs)
    
    def __get__(self, obj, type=None):
        return self.__class__(self.f.__get__(obj, type))
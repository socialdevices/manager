from datetime import datetime
from django.core.cache import cache
from operator import itemgetter
from threading import Lock

import logging


logger = logging.getLogger(__name__)

class EventHandler():
    
    def __init__(self):
        # TODO
        cache.add('event_seq_num', 1, 60*60*24)
        self.memChdLock = Lock()    # write lock for memcached


    def add_event(self, description, date=None):
        event_dict = {}
        
        if date == None:
            date = datetime.now()
            
        event_dict['date'] = date.strftime('%Y-%m-%d %H:%M:%S')
        event_dict['description'] = description
    
        self.memChdLock.acquire()
        seq_num = cache.get('event_seq_num', 1)
        key = 'event_%i' % seq_num
        ret = cache.add(key, event_dict)

        cache.incr('event_seq_num')
        self.memChdLock.release()        
        
        
        return True
    
    def get_event(self, seq_num):
        key = 'event_%i' % seq_num
        return cache.get(key)
    
    def get_events(self, start_seq_num, end_seq_num):        
        keys = []
        for i in range(start_seq_num, end_seq_num):
            key = 'event_%i' % i
            keys.append(key)

        return map( itemgetter(1), sorted(cache.get_many(keys).items()) )
    
    def get_current_sequence_number(self):
        return cache.get('event_seq_num', 1)
        
    

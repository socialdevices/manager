from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie
from events.event import EventHandler
import json
import time



def index(request):
    return render_to_response('event_log.html', context_instance=RequestContext(request))

@ensure_csrf_cookie
def events(request):
    
    if request.is_ajax() and request.method == 'POST':
        event_handler = EventHandler()
        
        if 'latest' not in request.POST or request.POST['latest'] == 'null':
            latest_seq_num = event_handler.get_current_sequence_number()
        else:
            latest_seq_num = int(request.POST['latest'])
        
        start_timestamp = time.time()
        event_messages = {'events': [], 'latest': latest_seq_num}
        while start_timestamp + 20 > time.time():
            cur_seq_num =  event_handler.get_current_sequence_number()
            
            if latest_seq_num < cur_seq_num:
                events = event_handler.get_events(latest_seq_num, cur_seq_num)
                
                for event in events:
                    event_messages['events'].append({'msg': event['description'], 'date': event['date']})
                
                if len(event_messages['events']) > 0:
                    event_messages['latest'] = cur_seq_num
                    break
                
            time.sleep(3)
    
        data = json.dumps(event_messages)
        
        return HttpResponse(data, 'application/json')
    else:
        return HttpResponse('Invalid request')

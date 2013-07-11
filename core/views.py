from core.clients import CaasClient, CaasConnectionError, CaasTimeoutError, \
    CaasNotFoundError, CaasInternalServerError
from core.configuration_models import WcrlModelGenerator
from core.forms import UploadInterfaceFileForm, UploadActionFileForm, \
    UploadScheduleFileForm, ConfigurationForm
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from events.event import EventHandler
import json
import logging
import kurre.settings as settings
from models import Device
from recommenders import Recommender, RecommenderException

logger = logging.getLogger(__name__)
event_handler = EventHandler()

@csrf_exempt
@require_http_methods(['POST'])
def parse_interfaces(request):
    form = UploadInterfaceFileForm(request.POST, request.FILES)

    if form.is_valid():
        try:
            form.save()
        except Exception, e:
            return HttpResponseBadRequest(e)

        event_handler = EventHandler()
        event_handler.add_event(u'Interface file %s was uploaded and parsed successfully' % request.FILES['file'].name)
        logger.debug(u'Interface file %s was uploaded and parsed successfully' % request.FILES['file'].name)

        return HttpResponse(status=201)
    else:
        return HttpResponseBadRequest(json.dumps(form.errors), mimetype='application/json')


@csrf_exempt
@require_http_methods(['POST'])
def parse_actions(request):
    form = UploadActionFileForm(request.POST, request.FILES)

    if form.is_valid():
        try:
            form.save()
        except Exception, e:
            return HttpResponseBadRequest(e)

        event_handler = EventHandler()
        event_handler.add_event(u'Action file %s was uploaded and parsed successfully' % request.FILES['file'].name)
        logger.debug(u'Action file %s was uploaded and parsed successfully' % request.FILES['file'].name)

        return HttpResponse(status=201)
    else:
        return HttpResponseBadRequest(json.dumps(form.errors), mimetype='application/json')


@csrf_exempt
@require_http_methods(['POST'])
def parse_schedules(request):
    form = UploadScheduleFileForm(request.POST, request.FILES)

    if form.is_valid():
        try:
            form.save()
        except Exception, e:
            return HttpResponseBadRequest(e)

        event_handler = EventHandler()
        event_handler.add_event(u'Schedule file %s was uploaded and parsed successfully' % request.FILES['file'].name)
        logger.debug(u'Schedule file %s was uploaded and parsed successfully' % request.FILES['file'].name)

        return HttpResponse(status=201)
    else:
        return HttpResponseBadRequest(json.dumps(form.errors), mimetype='application/json')


@csrf_exempt
@require_http_methods(['POST'])
def get_configuration(request):
    #data = json.loads(request.raw_post_data)
    data = {'actions': request.raw_post_data}
    form = ConfigurationForm(data)

    if form.is_valid():
        # Deserialize the configuration request
        actions = simplejson.loads(data['actions'])
        
        # Create a new model generator and generate the configuration model
        # and configuration selections
        model_generator = WcrlModelGenerator()
        
        # test, whether we need to configure action-at-a-time (when any action in configuration request
        # contains preset roles)
        separate_actions = False
        client = CaasClient()
        
        for action in actions:
         #convert device external id:s to internal (wcrl does not support @:s)
            action['devices'] = map( lambda x: model_generator.get_dev_pk(x), action['devices'] )
            action['roles'] = map( lambda x: x if x == '_anyvalue_' else model_generator.get_dev_pk(x), action['roles'] )

            for role in action['roles']:
                if role != '_anyvalue_' and len(actions)>1:
                    separate_actions = True
                    break
            if separate_actions:
                break
            
        if separate_actions:
            configurations = []
            i=0
            for action in actions:
                wcrl_model = model_generator.generate_configuration_model(action)
                wcrl_selections = model_generator.generate_configuration_selections(action)
                
                try:
                    configuration = client.upload_and_get_wcrl_configuration('test', wcrl_model, wcrl_selections)
                except (CaasConnectionError, CaasTimeoutError, CaasNotFoundError, CaasInternalServerError), e:
                    logger.error('The request to Caas failed: {0}'.format(e))
                    event_handler.add_event('The request to Caas failed: {0}'.format(e))
                    return HttpResponseBadRequest()

                if configuration == None:
                    continue
                
                configurations += configuration
            
        else:            
            wcrl_model = model_generator.generate_configuration_model(actions)
            wcrl_selections = model_generator.generate_configuration_selections(actions)
            model_name = 'test'
            
            try:
                configurations = client.upload_and_get_wcrl_configuration(model_name, wcrl_model, wcrl_selections)
            except (CaasConnectionError, CaasTimeoutError, CaasNotFoundError, CaasInternalServerError), e:
                logger.error('The request to Caas failed: {0}'.format(e))
                event_handler.add_event('The request to Caas failed: {0}'.format(e))
                return HttpResponseBadRequest()
            else:
                event_handler.add_event('Configuration request for model {0} with selections {1} sent to Caas'.format(model_name, wcrl_selections))
        
        if configurations == None:
            return HttpResponse(status=204)

        # let's create a simple random-largest -recommender
        try:
            recommender = Recommender()
            selected = recommender.recommend( configurations )
        except RecommenderException, e:
            logger.debug( 'Caught recommender exception: {0}'.format(e) )
            selected = random.choice( configurations )[0]
        
        # clear out the added string elements for configuration
        ret = {}
        ret_data = {'roles':[]}
        ret_data['action'] = selected['action_name'].replace('action_','')
        #convert internal ids back
        ret_data['roles'] = map(lambda x: Device.objects.get(pk=x.items()[0][1].replace('id','')).id_string , sorted(selected['roles']))
        
        # Pass the parameters for initiated function (why? shouldn't be necessary, since the controller knows these already)
        for initial_action in actions:
            if ret_data['action'] in initial_action.values():
                ret = dict( initial_action.items() + ret_data.items() )
                break

        if 'devices' in ret.keys():
            del ret['devices']
            
        return HttpResponse( json.dumps(ret), content_type='application/json', status=200)
    
    else:
        return HttpResponseBadRequest(json.dumps(form.errors), mimetype='application/json')

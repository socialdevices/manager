from django.conf import settings
from django.template.loader import render_to_string
from events.event import EventHandler
from xml.dom import minidom
import json
import logging
import requests
import socket

logger = logging.getLogger(__name__)
event_handler = EventHandler()

class ProximityClient(object):
    
    def __init__(self):
        self.host = settings.PROXIMITY_SERVER['default']['HOST']
        self.port = settings.PROXIMITY_SERVER['default']['PORT']
        self.socket = None
    
    def _connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
        except socket.error, e:
            if e.errno == 111:
                raise ProximityClientConnectionError("The connection to the proximity server at %s:%i was refused" % (self.host, self.port))
        else:
            return True
    
    def _close(self):
        self.socket.close()
    
    def _send_request(self, request):
        if self._connect():
            self.socket.send(request)
            response = self.socket.recv(1024)
            self._close()
            
            return response
        
    def add_device(self, mac_address):
        self._send_request("add_device, " + mac_address)
    
    def set_group(self, mac_address, neighbours):
        self._send_request("set_group, " + mac_address + "," + ",".join(neighbours))
    
    def get_group(self, mac_address):
        response = self._send_request("get_group, " + mac_address)
        
        return ([], response.split(","))[response != "[]"]
    
    def flush(self):
        self._send_request("flush")
            

class ProximityClientError(Exception):
    """Base class for proximity client errors."""
    pass

class ProximityClientConnectionError(ProximityClientError):
    """Used to indicate that a connection could not be established with the proximity server."""
    pass



class MirriClient(object):
    
    def __init__(self):
        self.host = settings.MIRRI['HOST']
        self.port = settings.MIRRI['PORT']
        self.base_url = 'http://%s:%s' % (self.host, self.port)
    
    def _send_request(self, method, url, **kwargs):
        try:
            response = requests.request(method, url, **kwargs)
        except requests.ConnectionError:
            raise MirriConnectionError('The connection to Mirri at %s failed' % url)
        except requests.Timeout:
            raise MirriTimeoutError('The request to Mirri at %s timed out' % url)
        else:
            if response.status_code == 404:
                raise MirriNotFoundError('Url %s not found for Mirri' % url)
            return response
    
    def start_action(self, action_name, init_parameters, body_parameters):
        """ Format of init and body parameters:
            A list of devices and optional parameters at the end
            [{'deviceIdentity': 'aa:aa:aa:aa:aa:aa', 'deviceName': 'Device one', 'interfaceNames': ['TalkingDevice']},
             {'deviceIdentity': 'bb:bb:bb:bb:bb:bb', 'deviceName': 'Device two', 'interfaceNames': ['TalkingDevice']},
             1234] """
        
        path = '/api/action/trigger/%s' % action_name
        url = self.base_url + path
        data = {'init_parameters': json.dumps(init_parameters), 'body_parameters': json.dumps(body_parameters)}
        response = self._send_request('post', url, data=data)
        return response.content
    
    def upload_interface_file(self, interface_name, interface_file):
        path = '/api/device/upload/%s' % interface_name
        url = self.base_url + path
        files = {'interface_file': interface_file}
        self._send_request('post', url, files=files, timeout=10)
    
    def upload_action_file(self, action_file):
        path = '/api/action/upload'
        url = self.base_url + path
        files = {'action_class_file': action_file}
        self._send_request('post', url, files=files, timeout=10)

class MirriError(Exception):
    """Base class for Mirri client errors."""
    pass

class MirriConnectionError(MirriError):
    """Used to indicate that a connection to Mirri failed."""
    pass

class MirriTimeoutError(MirriError):
    """Used to indicate that a connection to Mirri timed out."""
    pass

class MirriNotFoundError(MirriError):
    """Used to indicate that a HTTP 404 Not Found was received."""
    pass





class CaasClient(object):
    
    def __init__(self):
        self.host = settings.CAAS['HOST']
        self.port = settings.CAAS['PORT']
        self.base_url = 'http://%s:%s' % (self.host, self.port)
    
    def _send_request(self, method, url, **kwargs):
        try:
            response = requests.request(method, url, **kwargs)
        except requests.ConnectionError:
            raise CaasConnectionError('The connection to Caas at %s failed' % url)
        except requests.Timeout:
            raise CaasTimeoutError('The request to Caas at %s timed out' % url)
        else:
            if response.status_code == 404:
                raise CaasNotFoundError('Url %s not found for Caas' % url)
            return response
    
    def _parse_caas_configuration(self, configuration_xml):
        if configuration_xml == '':
            logger.debug('CaaS WCRL configuration response was empty!')
            return None
                        
        configurations = []
        dom = minidom.parseString(configuration_xml)
            
        for config in dom.getElementsByTagName('Configuration'):
                    
            configuration = { 'roles': [] }
            #configuration['roleCount'] = config.getAttribute('roleCount')

            for action_node in config.getElementsByTagName('action'):
                action_name = action_node.getAttribute('name')
                if action_name != '':
                    configuration['action_name'] = action_name
                
                else:
                    logger.debug('empty action name in wcrl configuration response!')
                    return None

                for role_node in action_node.getElementsByTagName('role'):
                    role = {}
                    for node in role_node.childNodes:
                        if node.nodeType == node.TEXT_NODE:
                            role[role_node.getAttribute('name')] = role_node.firstChild.nodeValue
                    configuration['roles'].append(role)
            
            configurations.append( configuration )
        
        return configurations

    
    def get_configuration(self, model_name, selections):
        """ Format of selections:
            [{'name': u'isInProximity_aa_aa_aa_aa_aa_aa', 'value': 'yes'}, 
             {'name': u'isWilling_aa_aa_aa_aa_aa_aa', 'value': 'yes'}, 
             {'name': u'isSilent_aa_aa_aa_aa_aa_aa', 'value': 'yes'},
             {'name': u'isInProximity_bb_bb_bb_bb_bb_bb', 'value': 'no'}, 
             {'name': u'isWilling_bb_bb_bb_bb_bb_bb', 'value': 'yes'}, 
             {'name': u'isSilent_bb_bb_bb_bb_bb_bb', 'value': 'no'}]} 
            
            Format of return value:
            {'action_name': 'Dialog', 'devices': ['aa:aa:aa:aa:aa:aa', 'bb:bb:bb:bb:bb:bb']}
            """
        
        path = '/KumbangConfigurator'
        url = self.base_url + path
        headers = {'content-type': 'application/xml'}
        
        payload_list = []
        payload_list.append('<xml>')
        payload_list.append('<model name="')
        payload_list.append(model_name)
        payload_list.append('"/>')
        payload_list.append('<configuration><feature name="root" type="Status">')
        
        for selection in selections:
            payload_list.append('<attribute name="')
            payload_list.append(selection['name'])
            payload_list.append('">')
            payload_list.append(selection['value'])
            payload_list.append('</attribute>')
        
        payload_list.append('</feature></configuration>')
        payload_list.append('</xml>')
        payload = ''.join(payload_list)

        # Send request
        response = self._send_request('post', url, data=payload, headers=headers)

        configuration_xml = response.content
        configuration = {'action_name': '', 'devices': []}

        if response.status_code == 200:
            pass

        else:
            raise CaasInternalServerError(response.content)

        return configuration

    def upload_configuration_model(self, model_name, model):
        path = '/KumbangConfigurator'
        url = self.base_url + path
        headers = {'content-type': 'application/xml'}

        payload_list = []
        payload_list.append('<xml>')
        payload_list.append('<model name="')
        payload_list.append(model_name)
        payload_list.append('">')
        payload_list.append(model)
        payload_list.append('</model></xml>')
        payload = ''.join(payload_list)

        # Send request
        response = self._send_request('post', url, data=payload, headers=headers, timeout=10)

        if response.status_code == 201:
            event_handler.add_event('Model %s sent to Caas: %s' % (model_name, payload))
        else:
            raise CaasInternalServerError(response.content)

    def upload_wcrl_model(self):
        pass

    def get_wcrl_configuration(self):
        pass

    def upload_and_get_wcrl_configuration(self, model_name, model, selections):
        path = '/wcrl'
        url = self.base_url + path
        headers = {'content-type': 'application/xml'}

        ctx_dict = {'model_name': model_name, 'model_format': 'wcrl_lparse', 
                    'model': model, 'selections': selections}
        payload = render_to_string('clients/caas/model_configuration_request.xml',
                                   ctx_dict)

        #logger.debug('WCRL configuration request: {0}'.format(payload))
        # Send request
        response = self._send_request('post', url, data=payload,
                                      headers=headers, timeout=10)

        event_handler.add_event('WCRL configuration request sent to Caas!')
        logger.debug('WCRL configuration request sent to Caas!')

        if response.status_code == 200:
            configurations = self._parse_caas_configuration( response.content )

            if configurations:
                return configurations

            else:
                logger.error( "Caas configuration reply could not be parsed.")
                raise CaasReplyParseError(response.content)

        elif response.status_code == 204:
            logger.debug( 'No configurations could be found for request' )
            return None

        else:
            event_handler.add_event('WCRL configuration request to Caas failed!')
            logger.debug('Failed WCRL configuration request: {0}'.format(payload))
            raise CaasInternalServerError(response.content)
            


class CaasError(Exception):
    """Base class for Caas client errors."""
    pass


class CaasConnectionError(CaasError):
    """Used to indicate that a connection to Caas failed."""
    pass


class CaasTimeoutError(CaasError):
    """Used to indicate that a connection to Caas timed out."""
    pass


class CaasNotFoundError(CaasError):
    """Used to indicate that a HTTP 404 Not Found was received."""
    pass


class CaasInternalServerError(CaasError):
    """Used to indicate that a HTTP 500 Internal Server Error was received."""
    pass
    
class CaasReplyParseError(CaasError):
    """Used to indicate that Caas reply could not be parsed."""
    pass

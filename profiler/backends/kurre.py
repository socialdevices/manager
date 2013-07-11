from datetime import datetime
from default import DefaultProfiler
from django.core import management
from profiler.backends.default import ProfilingCallError
import json
import logging
import requests

logger = logging.getLogger(__name__)

class KurreProfiler(DefaultProfiler):
    
    def __init__(self, num_runs, first, num_requests, increment, condition):
        super(KurreProfiler, self).__init__(num_runs, first, num_requests, increment, condition)
    
    def _send_request(self, method, url, **kwargs):
        try:
            response = requests.request(method, url, **kwargs)
        except requests.ConnectionError:
            raise KurreConnectionError('The connection to Kurre at %s failed' % url)
        except requests.Timeout:
            raise KurreTimeoutError('The request to Kurre at %s timed out' % url)
        else:
            if response.status_code == 404:
                raise KurreNotFoundError('Url %s not found for Kurre' % url)
            return response
        
    def _create_mac_address(self, number):
        hex_number = '%012x' % number
        mac_address = ':'.join([hex_number[x:x+2] for x in range(0, len(hex_number), 2)])
        
        return mac_address
    
    def _first_request(self):
        path = '/admin/'
        url = self.base_url + path
        logger.debug('Sending first request')
        response = self._send_request('get', url)
        
        if response.status_code == 200:
            logger.debug('First request successful')
            return True
        else:
            logger.error('First request not successful: HTTP %i' % response.status_code)
            return False
    
    def profile_add_device(self, call_num):
        # called multiple times in a group run
        #self.db.update_profiler_group_run_x_label(group_id, "devices")
        
        mac_address = self._create_mac_address(call_num)
        
        path = '/api/v2/device/'
        url = self.base_url + path
        payload = {'mac_address': mac_address, 'name': 'Device %i' % call_num}
        headers = {'content-type': 'application/json'}
        
        try:
            response = self._send_request('post', url, data=json.dumps(payload), headers=headers)
        except (KurreConnectionError, KurreTimeoutError, KurreNotFoundError), e:
            logger.error(e)
            return False
        else:
            if response.status_code != 201:
                logger.error('Request %i not successful: HTTP %i - %s' % (call_num, response.status_code, response.content))
                return False
            
            return True
            
    def teardown_add_device(self, num_calls):
        self._del_devices(num_calls)

    def profile_add_device_and_interface(self, call_num):
        #self.db.update_profiler_group_run_x_label(group_id, "device interfaces")
        
        error = False
        
        mac_address = self._create_mac_address(call_num)
        
        path = '/api/v2/device/'
        url = self.base_url + path
        payload = {'mac_address': mac_address, 'name': 'Device %i' % call_num}
        headers = {'content-type': 'application/json'}
        
        try:
            response = self._send_request('post', url, data=json.dumps(payload), headers=headers)
        except (KurreConnectionError, KurreTimeoutError, KurreNotFoundError), e:
            logger.error(e)
            error = True
        else:
            if response.status_code != 201:
                logger.error('Device %s not added successfully: HTTP %i - %s' % (mac_address, response.status_code, response.content))
                error = True
        
        path = '/api/v2/device/' + mac_address + '/interface/'
        url = self.base_url + path
        payload = {'interface_name': 'TalkingDevice'}
        headers = {'content-type': 'application/json'}
        
        try:
            response = self._send_request('post', url, data=json.dumps(payload), headers=headers)
        except (KurreConnectionError, KurreTimeoutError, KurreNotFoundError), e:
            logger.error(e)
            error = True
        else:
            if response.status_code != 201:
                logger.error('Interface not added successfully for devices %s: %i - %s' % (mac_address, response.status_code, response.content))
                error = True
        
        return not error
    
    def teardown_add_device_and_interface(self, num_calls):
        self._del_devices(num_calls)
        
    def profile_trigger_configuration(self, call_num):
        #self.db.update_profiler_group_run_x_label(group_id, "device interfaces")
        
        error = False
        
        mac_address = self._create_mac_address(call_num)
        
        path = '/api/v2/device/'
        url = self.base_url + path
        payload = {'mac_address': mac_address, 'name': 'Device %i' % call_num}
        headers = {'content-type': 'application/json'}
        
        try:
            response = self._send_request('post', url, data=json.dumps(payload), headers=headers)
        except (KurreConnectionError, KurreTimeoutError, KurreNotFoundError), e:
            logger.error(e)
            error = True
        else:
            if response.status_code != 201:
                logger.error('Device %s not added successfully: HTTP %i - %s' % (mac_address, response.status_code, response.content))
                error = True
        
        path = '/api/v2/device/' + mac_address + '/interface/'
        url = self.base_url + path
        payload = {'interface_name': 'TalkingDevice'}
        headers = {'content-type': 'application/json'}
        
        try:
            response = self._send_request('post', url, data=json.dumps(payload), headers=headers)
        except (KurreConnectionError, KurreTimeoutError, KurreNotFoundError), e:
            logger.error(e)
            error = True
        else:
            if response.status_code != 201:
                logger.error('Interface not added successfully for device %s: %i - %s' % (mac_address, response.status_code, response.content))
                error = True
        
        
        path = '/api/v2/device/' + mac_address + '/interface/TalkingDevice/method/'
        url = self.base_url + path
        payload = {'method_name': 'isWilling', 'value': True}
        headers = {'content-type': 'application/json'}
        
        try:
            response = self._send_request('post', url, data=json.dumps(payload), headers=headers)
        except (KurreConnectionError, KurreTimeoutError, KurreNotFoundError), e:
            logger.error(e)
            error = True
        else:
            if response.status_code != 201:
                logger.error('State value not added successfully for device %s: %i - %s' % (mac_address, response.status_code, response.content))
                error = True
        
        
        path = '/api/v2/device/' + mac_address + '/interface/TalkingDevice/method/'
        url = self.base_url + path
        payload = {'method_name': 'isSilent', 'value': True}
        headers = {'content-type': 'application/json'}
        
        try:
            response = self._send_request('post', url, data=json.dumps(payload), headers=headers)
        except (KurreConnectionError, KurreTimeoutError, KurreNotFoundError), e:
            logger.error(e)
            error = True
        else:
            if response.status_code != 201:
                logger.error('State value not added successfully for device %s: %i - %s' % (mac_address, response.status_code, response.content))
                error = True
        
        return not error
    
    def teardown_trigger_configuration(self, num_calls):
        self._del_devices(num_calls)
    
    def _del_devices(self, num):
        logger.debug('Deleting the devices that were added (does not affect statistics)')
        
        for i in range(1, num + 1):
            mac_address = self._create_mac_address(i)
            
            path = '/api/v2/device/%s/' % mac_address
            url = self.base_url + path
            response = self._send_request('delete', url)
            
            if response.status_code == 204:
                logger.debug('Device %s deleted successfully' % mac_address)
            else:
                logger.error('Device %s could not be deleted: HTTP %i - %s' % (mac_address, response.status_code, response.content))        
        logger.debug('Deleted %i devices' % num)
        
        management.call_command('flushproximityserver')


class KurreError(Exception):
    """Base class for Kurre client errors."""
    pass

class KurreConnectionError(KurreError):
    """Used to indicate that a connection to Kurre failed."""
    pass

class KurreTimeoutError(KurreError):
    """Used to indicate that a connection to Kurre timed out."""
    pass

class KurreNotFoundError(KurreError):
    """Used to indicate that a HTTP 404 Not Found was received."""
    pass
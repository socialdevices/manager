from core.clients import ProximityClient
from core.models import Device, DeviceInterface, Interface, Method, StateValue
from django.conf import settings
from django.test import TestCase
import json

class DeviceStateValueAPITestCase(TestCase):
    fixtures = ['devices_testdata']
    
    def setUp(self):
        self.old_setting = settings.PROXIMITY_SERVER['default']
        settings.PROXIMITY_SERVER['default'] = settings.PROXIMITY_SERVER['test']
        self.proximity_client = ProximityClient()
        self.proximity_client.flush()
        
    def tearDown(self):
        settings.PROXIMITY_SERVER['default'] = self.old_setting
    
    def test_good_device_statevalue_post(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TalkingDevice'
        method_name = 'isSilent'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check that the device interface actually exists
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        
        # Check that the method exists for the interface
        self.assertTrue(Method.objects.filter(interface__name=interface_name, name='isSilent').exists())
        
        # Check the initial amount of state values for the device in the database
        self.assertEqual(StateValue.objects.filter(device__mac_address=mac_address).count(), 2)
        
        # The state value data without arguments
        payload = json.dumps({'method_name': method_name, 'value': False})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Location'], 'http://testserver/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        
        
        interface_name = 'CalendarSource'
        method_name = 'eventApproaching'
        
        # The state value data with arguments
        payload = json.dumps({'method_name': method_name, 'arguments': {'eid': '1234'}, 'value': False})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Location'], 'http://testserver/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        
        
        interface_name = 'ScreenDevice'
        method_name = 'screenAvailable'
        
        # The state value data with an empty argument dictionary
        payload = json.dumps({'method_name': method_name, 'arguments': {}, 'value': False})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Location'], 'http://testserver/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        
        
        # Check the final amount of state values for the device in the database
        self.assertEqual(StateValue.objects.filter(device__mac_address=mac_address).count(), 5)
        
    def test_bad_device_statevalue_posts(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TalkingDevice'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check that the device interface actually exists
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        
        # Check that the method exists for the interface
        self.assertTrue(Method.objects.filter(interface__name=interface_name, name='isSilent').exists())
        
        # Check the initial amount of state values for the device in the database
        self.assertEqual(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name).count(), 1)
        
        
        # Send post without data and check that the response is 400 Bad Request
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['method_name'], 'Method name is a required field')
        self.assertEqual(content['value'], 'Value is a required field')
        
        
        # Send post without method name and check that the response is 400 Bad Request
        payload = json.dumps({'value': False})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['method_name'], 'Method name is a required field')
        
        
        # Send post without value and check that the response is 400 Bad Request
        payload = json.dumps({'method_name': 'isSilent'})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['value'], 'Value is a required field')
        
        
        # Send junk data and check that the response is 400 Bad Request
        payload = json.dumps({'foo': 'bar'})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['method_name'], 'Method name is a required field')
        self.assertEqual(content['value'], 'Value is a required field')
        
        
        # Send post with non-existent method name and check that the response is 400 Bad Request
        payload = json.dumps({'method_name': 'fooBarMethod', 'value': False})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['method_name'], 'Method fooBarMethod does not exist.')
        
        
        # Send post with empty method name
        payload = json.dumps({'method_name': '', 'value': False})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['method_name'], 'Method name cannot be an empty string')
        
        
        # Send post without arguments for a state value that requires arguments
        payload = json.dumps({'method_name': 'eventApproaching', 'value': False})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/CalendarSource/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['arguments'], 'eid is missing from arguments.')
        
        
        # Send post with arguments for a state value that does not require any arguments
        payload = json.dumps({'method_name': 'isWilling', 'arguments': {'eid': '1234'}, 'value': False})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['arguments'], 'Method isWilling does not accept eid as an argument.')
        
        
        # Send post with extra arguments (same as the above)
        payload = json.dumps({'method_name': 'eventApproaching', 'arguments': {'eid': '1234', 'test': '12345'}, 'value': False})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/CalendarSource/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['arguments'], 'Method eventApproaching does not accept test as an argument.')
        
        
        # Send post for non-existent device
        payload = json.dumps({'method_name': 'isSilent', 'value': False})
        response = self.client.post('/api/v2/device/aa:bb:cc:dd:ee:ff/interface/' + interface_name + '/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 404)
        content = json.loads(response.content)
        self.assertEqual(content['error_message'], 'Sorry, this request could not be processed. Please try again later.')
        
        
        # Send post for non-existent interface
        payload = json.dumps({'method_name': 'isSilent', 'value': False})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/fooBarInterface/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 404)
        content = json.loads(response.content)
        self.assertEqual(content['error_message'], 'Sorry, this request could not be processed. Please try again later.')
        
        
        # Send post with a state value that already exists for the specific device in the database
        self.assertTrue(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name='TalkingDevice', method__name='isWilling').exists())
        payload = json.dumps({'method_name': 'isWilling', 'value': False})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['method_name'], 'Duplicate method. Device aa:aa:aa:aa:aa:aa has already added a value for method isWilling in interface TalkingDevice.')
        
        
        # Send post for interface that exists, but is not bound with the device
        self.assertTrue(Interface.objects.filter(name='CalendarDevice').exists())
        payload = json.dumps({'method_name': 'hasEvents', 'value': False})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/CalendarDevice/method/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['method_name'], 'Device aa:aa:aa:aa:aa:aa does not have the appropriate interface for being able to store a state value for method hasEvents.')
        
        # Check the final amount of state values for the device in the database
        self.assertEqual(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name).count(), 1)
        
    def test_good_device_statevalue_delete(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TalkingDevice'
        method_name = 'isWilling'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check that the device interface actually exists
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        
        # Check that the method exists for the interface
        self.assertTrue(Method.objects.filter(interface__name=interface_name, name=method_name).exists())
        
        # Check the initial amount of state values for the device in the database
        self.assertEqual(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name).count(), 1)
        
        # Check that the state value actually exists in the database
        self.assertTrue(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name, method__name=method_name).exists())
        
        # Issue a DELETE request
        response = self.client.delete('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        
        # Check that the response is 204 No Content
        self.assertEqual(response.status_code, 204)
        
        # Check that the state value does not exist in the database anymore
        self.assertFalse(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name, method__name=method_name).exists())
        
        # Check the final amount of state values for the device in the database
        self.assertEqual(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name).count(), 0)
        
        # TODO: cascade check
    
    def test_bad_device_statevalue_deletes(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TalkingDevice'
        method_name = 'isWilling'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check that the device interface actually exists
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        
        # Check that the method exists for the interface
        self.assertTrue(Method.objects.filter(interface__name=interface_name, name=method_name).exists())
        
        # Check the initial amount of state values for the device in the database
        self.assertEqual(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name).count(), 1)
        
        
        # Ensure that the deletion of a non-existent state value throws 404 Not Found
        self.assertFalse(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name, method__name='fooBarMethod').exists())
        response = self.client.delete('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/fooBarMethod/')
        self.assertEqual(response.status_code, 404)
        
        
        # Ensure that the deletion of a state value of a non-existent device throws 404 Not Found
        self.assertFalse(Device.objects.filter(mac_address='aa:bb:cc:dd:ee:ff').exists())
        response = self.client.delete('/api/v2/device/aa:bb:cc:dd:ee:ff/interface/' + interface_name + '/method/' + method_name + '/')
        self.assertEqual(response.status_code, 404)
        
        
        # Ensure that the deletion of a state value of a non-existent interface throws 404 Not Found
        self.assertFalse(Interface.objects.filter(name='FooBarInterface').exists())
        response = self.client.delete('/api/v2/device/' + mac_address + '/interface/FooBarInterface/method/' + method_name + '/')
        self.assertEqual(response.status_code, 404)
        
        
        # The deletion of all device state values should throw 405 Method Not Allowed
        response = self.client.delete('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/')
        self.assertEqual(response.status_code, 405)
        
        
        # Check that the final amount of state values that the device has in the database is the same as in the beginning
        self.assertEqual(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name).count(), 1)
    
    
    def test_good_device_statevalue_get_list(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TalkingDevice'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check that the device interface actually exists
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        
        # Check the initial amount of state values for the device in the database
        self.assertEqual(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name).count(), 1)
        
        # Get a list of devices including their information
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/')
        
        # Check that the response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Convert the json to python
        content = json.loads(response.content)
        
        # Check that all the state values of the device are in the list
        self.assertEqual([statevalue['method_name'] for statevalue in content['objects']], ['isWilling'])
        
        # Check that the number of state values in the list is 1
        self.assertEqual(len(content['objects']), 1)
        
    
    def test_good_device_statevalue_get_detail(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TalkingDevice'
        method_name = 'isWilling'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check that the device interface actually exists
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        
        # Check that the method exists for the interface
        self.assertTrue(Method.objects.filter(interface__name=interface_name, name=method_name).exists())
        
        # Check that the state value actually exists in the database
        self.assertTrue(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name, method__name=method_name).exists())
        
        # Get the information related to one state value
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        
        # Check that the response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that the values are correct
        content = json.loads(response.content)
        self.assertEqual(content['arguments'], {})
        self.assertEqual(content['created_at'], '2011-12-20T17:10:41.314132')
        self.assertEqual(content['method_name'], 'isWilling')
        self.assertEqual(content['resource_uri'], '/api/v2/device/aa:aa:aa:aa:aa:aa/interface/TalkingDevice/method/isWilling/')
        self.assertEqual(content['updated_at'], '2011-12-20T17:10:41.314132')
        self.assertEqual(content['value'], 'False')
        
        
        
        interface_name = 'ScreenDevice'
        method_name = 'hasNext'
        
        # Check that the device interface actually exists
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        
        # Check that the method exists for the interface
        self.assertTrue(Method.objects.filter(interface__name=interface_name, name=method_name).exists())
        
        # Check that the state value actually exists in the database
        self.assertTrue(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name, method__name=method_name).exists())
        
        # Get the information related to one state value
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        
        # Check that the response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that the values are correct
        content = json.loads(response.content)
        self.assertEqual(content['arguments'], {'screenId': '1234'})
        self.assertEqual(content['created_at'], '2011-12-20T17:10:41.314132')
        self.assertEqual(content['method_name'], 'hasNext')
        self.assertEqual(content['resource_uri'], '/api/v2/device/aa:aa:aa:aa:aa:aa/interface/ScreenDevice/method/hasNext/')
        self.assertEqual(content['updated_at'], '2011-12-20T17:10:41.314132')
        self.assertEqual(content['value'], 'False')
    
    def test_bad_device_statevalue_get_details(self):
        
        # Get a state value for a non-existent interface method
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TalkingDevice'
        method_name = 'fooBarMethod'
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        self.assertFalse(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name, method__name=method_name).exists())
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        self.assertEqual(response.status_code, 404)
        
        
        # Get a state value for a non-existent device
        mac_address = 'aa:bb:cc:dd:ee:ff'
        interface_name = 'TalkingDevice'
        method_name = 'isWilling'
        self.assertFalse(Device.objects.filter(mac_address=mac_address).exists())
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        self.assertEqual(response.status_code, 404)
        
        
        # Get a state value for a non-existent interface
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'FooBarInterface'
        method_name = 'isWilling'
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        self.assertFalse(Interface.objects.filter(name=interface_name).exists())
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        self.assertEqual(response.status_code, 404)
    
    
    def test_good_device_statevalue_update(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TalkingDevice'
        method_name = 'isWilling'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check that the device interface actually exists
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        
        # Check that the method exists for the interface
        self.assertTrue(Method.objects.filter(interface__name=interface_name, name=method_name).exists())
        
        # Check that the state value actually exists in the database
        self.assertTrue(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name, method__name=method_name).exists())
        
        
        # Send a put request to update the value of isWilling to True
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['value'], 'False')
        payload = json.dumps({'value': 'True'})
        response = self.client.put('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/', payload, 'application/json')
        self.assertEqual(response.status_code, 204)
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['value'], 'True')
        
        
        # Send a put request to update the value of isWilling to True with an empty argument dictionary
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['value'], 'True')
        payload = json.dumps({'arguments': {}, 'value': 'False'})
        response = self.client.put('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/', payload, 'application/json')
        self.assertEqual(response.status_code, 204)
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['value'], 'False')
        
        
        interface_name = 'ScreenDevice'
        method_name = 'hasNext'
        
        # Send a put request to update the value of eventApproaching to True with arguments
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['value'], 'False')
        self.assertEqual(content['arguments']['screenId'], '1234')
        payload = json.dumps({'arguments': {'screenId': '12345'}, 'value': 'True'})
        response = self.client.put('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/', payload, 'application/json')
        self.assertEqual(response.status_code, 204)
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['value'], 'True')
        self.assertEqual(content['arguments']['screenId'], '12345')
    
    
    def test_bad_device_statevalue_updates(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TalkingDevice'
        method_name = 'isWilling'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check that the device interface actually exists
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        
        # Check that the method exists for the interface
        self.assertTrue(Method.objects.filter(interface__name=interface_name, name=method_name).exists())
        
        # Check that the state value actually exists in the database
        self.assertTrue(StateValue.objects.filter(device__mac_address=mac_address, method__interface__name=interface_name, method__name=method_name).exists())
        
        
        # Send a put request to update the method name
        payload = json.dumps({'method_name': 'fooBarMethod'})
        response = self.client.put('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['method_name'], 'Method name cannot be updated')
        
        
        # Send a put request to update the created_at field
        payload = json.dumps({'created_at': '2011-12-22T16:21:43.834112'})
        response = self.client.put('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['created_at'], 'Created at cannot be updated')
        
        
        # Send a put request to update the updated_at field
        payload = json.dumps({'updated_at': '2011-12-22T16:21:43.834112'})
        response = self.client.put('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['updated_at'], 'Updated at cannot be updated')
        
        
        # Send a put request without arguments for a state value that requires arguments
        payload = json.dumps({'value': False})
        response = self.client.put('/api/v2/device/' + mac_address + '/interface/ScreenDevice/method/hasNext/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['arguments'], 'screenId is missing from arguments.')
        
        
        # Send a put request with arguments for a state value that does not require any arguments
        payload = json.dumps({'arguments': {'eid': '1234'}, 'value': False})
        response = self.client.put('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/method/' + method_name + '/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['arguments'], 'Method isWilling does not accept eid as an argument.')
        
        
        # Send a put request with extra arguments (same as the above)
        payload = json.dumps({'arguments': {'screenId': '1234', 'test': '12345'}, 'value': False})
        response = self.client.put('/api/v2/device/' + mac_address + '/interface/ScreenDevice/method/hasNext/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['arguments'], 'Method hasNext does not accept test as an argument.')
        
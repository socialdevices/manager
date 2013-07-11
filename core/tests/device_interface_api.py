from core.clients import ProximityClient
from core.models import DeviceInterface, Device
from django.conf import settings
from django.test import TestCase
import json

class DeviceInterfaceAPITestCase(TestCase):
    fixtures = ['devices_testdata']
    
    def setUp(self):
        self.old_setting = settings.PROXIMITY_SERVER['default']
        settings.PROXIMITY_SERVER['default'] = settings.PROXIMITY_SERVER['test']
        self.proximity_client = ProximityClient()
        self.proximity_client.flush()
        
    def tearDown(self):
        settings.PROXIMITY_SERVER['default'] = self.old_setting
    
    def test_good_device_interface_post(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check the initial amount of interfaces that the device has in the database
        self.assertEqual(DeviceInterface.objects.filter(device__mac_address=mac_address).count(), 4)
        
        # The interface data
        payload = json.dumps({'interface_name': 'CalendarDevice'})
        
        # Issue a POST request
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/', payload, 'application/json')
        
        # Check that the response is 201 Created
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Location'], 'http://testserver/api/v2/device/' + mac_address + '/interface/CalendarDevice/')
        
        # Check the final amount of devices in the database
        self.assertEqual(DeviceInterface.objects.filter(device__mac_address=mac_address).count(), 5)
    
    def test_bad_device_interface_posts(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check the initial amount of interfaces that the device has in the database
        self.assertEqual(DeviceInterface.objects.filter(device__mac_address=mac_address).count(), 4)
        
        # Send post without data and check that the response is 400 Bad Request
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['interface_name'], 'Interface name is a required field')
        
        
        # Send post without interface name and check that the response is 400 Bad Request
        payload = json.dumps({})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['interface_name'], 'Interface name is a required field')
        
        
        # Send junk data and check that the response is 400 Bad Request
        payload = json.dumps({'foo': 'bar'})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['interface_name'], 'Interface name is a required field')
        
        
        # Send post with non-existent interface name and check that the response is 400 Bad Request
        payload = json.dumps({'interface_name': 'FooBarInterface'})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['interface_name'], 'Interface FooBarInterface does not exist.')
    
        
        # Send post with empty interface name
        payload = json.dumps({'interface_name': ''})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['interface_name'], 'Interface name cannot be an empty string')
        
        
        # Send post for non-existent device
        payload = json.dumps({'interface_name': 'TalkingDevice'})
        response = self.client.post('/api/v2/device/aa:bb:cc:dd:ee:ff/interface/', payload, 'application/json')
        self.assertEqual(response.status_code, 404)
        content = json.loads(response.content)
        self.assertEqual(content['error_message'], 'Sorry, this request could not be processed. Please try again later.')
    
        
        # Send post with an interface name that already exists for the specific device in the database
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name='TalkingDevice').exists())
        payload = json.dumps({'interface_name': 'TalkingDevice'})
        response = self.client.post('/api/v2/device/' + mac_address + '/interface/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['interface_name'], 'Duplicate interface. Device aa:aa:aa:aa:aa:aa already has interface TalkingDevice.')
        
        
        # Check the final amount of interfaces for the device in the database is the same as in the beginning
        self.assertEqual(DeviceInterface.objects.filter(device__mac_address=mac_address).count(), 4)
    
    
    def test_good_device_interface_delete(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TalkingDevice'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check the initial amount of interfaces that the device has in the database
        self.assertEqual(DeviceInterface.objects.filter(device__mac_address=mac_address).count(), 4)
        
        # Check that the device interface actually exists
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        
        # Issue a DELETE request
        response = self.client.delete('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/')
        
        # Check that the response is 204 No Content
        self.assertEqual(response.status_code, 204)
        
        # Check that the device interface does not exist in the database anymore
        self.assertFalse(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        
        # Check the final amount of device interfaces in the database
        self.assertEqual(DeviceInterface.objects.filter(device__mac_address=mac_address).count(), 3)
        
        # TODO: cascade check
    
    
    def test_bad_device_interface_deletes(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TalkingDevice'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check the initial amount of interfaces that the device has in the database
        self.assertEqual(DeviceInterface.objects.filter(device__mac_address=mac_address).count(), 4)
        
        
        # Ensure that the deletion of a non-existent device interface throws 404 Not Found
        self.assertFalse(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name='FooBarInterface').exists())
        response = self.client.delete('/api/v2/device/' + mac_address + '/interface/FooBarInterface/')
        self.assertEqual(response.status_code, 404)
        
        
        # Ensure that the deletion of an interface of a non-existent device throws 404 Not Found
        self.assertFalse(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name='FooBarInterface').exists())
        response = self.client.delete('/api/v2/device/aa:bb:cc:dd:ee:ff/interface/' + interface_name + '/')
        self.assertEqual(response.status_code, 404)
        
        
        # The deletion of all device interfaces should throw 405 Method Not Allowed
        response = self.client.delete('/api/v2/device/' + mac_address + '/interface/')
        self.assertEqual(response.status_code, 405)
        
        
        # Check the final amount of interfaces that the device has in the database is the same as in the beginning
        self.assertEqual(DeviceInterface.objects.filter(device__mac_address=mac_address).count(), 4)
    
    
    def test_good_device_interface_get_list(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check the initial amount of interfaces that the device has in the database
        self.assertEqual(DeviceInterface.objects.filter(device__mac_address=mac_address).count(), 4)
        
        # Get a list of devices including their information
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/')
        
        # Check that the response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Convert the json to python
        content = json.loads(response.content)
        
        # Check that all the interfaces of the device are in the list
        self.assertEqual([deviceinterface['interface_name'] for deviceinterface in content['objects']], ['TalkingDevice', 'SingingDevice', 'CalendarSource', 'ScreenDevice'])
        
        # Check that the number of device interfaces in the list is 4
        self.assertEqual(len(content['objects']), 4)
    
    
    def test_good_device_interface_get_detail(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TalkingDevice'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check that the device interface actually exists
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        
        # Get the information related to one device interface
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/')
        
        # Check that the response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that the values are correct
        content = json.loads(response.content)
        self.assertEqual(content['created_at'], '2011-12-19T16:21:43.912345')
        self.assertEqual(content['interface_name'], 'TalkingDevice')
        self.assertEqual(content['resource_uri'], '/api/v2/device/aa:aa:aa:aa:aa:aa/interface/TalkingDevice/')
    
    
    def test_bad_device_interface_get_details(self):
        
        # Get a device interface for a non-existent interface
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TestInterface'
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        self.assertFalse(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/')
        self.assertEqual(response.status_code, 404)
        
        # Get a device interface for a non-existent device
        mac_address = 'aa:bb:cc:dd:ee:ff'
        interface_name = 'TalkingDevice'
        self.assertFalse(Device.objects.filter(mac_address=mac_address).exists())
        self.assertFalse(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        response = self.client.get('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/')
        self.assertEqual(response.status_code, 404)
        
    def test_bad_device_interface_update(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        interface_name = 'TalkingDevice'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check that the device interface actually exists
        self.assertTrue(DeviceInterface.objects.filter(device__mac_address=mac_address, interface__name=interface_name).exists())
        
        # The device data to be updated
        payload = json.dumps({'interface_name': 'TestInterface'})
        
        # Issue a PUT request
        response = self.client.put('/api/v2/device/' + mac_address + '/interface/' + interface_name + '/', payload, 'application/json')
        
        # Check that the response is 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)
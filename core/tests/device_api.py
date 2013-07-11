from core.clients import ProximityClient
from core.models import Device
from django.conf import settings
from django.test import TestCase
import json

class DeviceAPITestCase(TestCase):
    fixtures = ['devices_testdata']

    def setUp(self):
        self.old_setting = settings.PROXIMITY_SERVER['default']
        settings.PROXIMITY_SERVER['default'] = settings.PROXIMITY_SERVER['test']
        self.proximity_client = ProximityClient()
        self.proximity_client.flush()
        
    def tearDown(self):
        settings.PROXIMITY_SERVER['default'] = self.old_setting
    
    def test_good_device_post(self):
        # Check the initial amount of devices in the database
        self.assertEqual(Device.objects.count(), 4)
        
        # The device data (mac_address, name)
        payload = json.dumps({'mac_address': 'aa:bb:cc:dd:ee:ff', 'name': 'Device one'})
        
        # Issue a POST request
        response = self.client.post('/api/v2/device/', payload, 'application/json')
        
        # Check that the response is 201 Created and that the location is correct
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Location'], 'http://testserver/api/v2/device/aa:bb:cc:dd:ee:ff/')
        
        # Check the final amount of devices in the database
        self.assertEqual(Device.objects.count(), 5)
    
    def test_bad_device_posts(self):
        # Check the initial amount of devices in the database
        self.assertEqual(Device.objects.count(), 4)
        
        
        # Send post without data and check that the response is 400 Bad Request
        response = self.client.post('/api/v2/device/', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['__all__'], 'Missing data')
        
        
        # Send post without mac address and check that the response is 400 Bad Request
        payload = json.dumps({'name': 'Device one'})
        response = self.client.post('/api/v2/device/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        
        
        # Send post without name and check that the response is 400 Bad Request
        payload = json.dumps({'mac_address': 'aa:bb:cc:dd:ee:ff'})
        response = self.client.post('/api/v2/device/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['name'], 'Device name is a required field')
        
        
        # Send junk data and check that the response is 400 Bad Request
        payload = json.dumps({'foo': 'bar'})
        response = self.client.post('/api/v2/device/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['mac_address'], 'Mac address is a required field')
        self.assertEqual(content['name'], 'Device name is a required field')
        
        
        # Send post with invalid mac address and check that the response is 400 Bad Request
        payload = json.dumps({'mac_address': 'aa:bb:cc:aa:ee:ff:tt', 'name': 'Device one'})
        response = self.client.post('/api/v2/device/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['mac_address'], 'Mac address format is incorrect')
        
        
        # Send post with a mac address that already exists in the database
        self.assertTrue(Device.objects.filter(mac_address='aa:aa:aa:aa:aa:aa').exists())
        payload = json.dumps({'mac_address': 'aa:aa:aa:aa:aa:aa', 'name': 'Device one'})
        response = self.client.post('/api/v2/device/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['mac_address'], 'Duplicate mac address. Mac address aa:aa:aa:aa:aa:aa already exists.')
        
        
        # Send post with empty name
        payload = json.dumps({'mac_address': 'aa:bb:cc:dd:ee:ff', 'name': ''})
        response = self.client.post('/api/v2/device/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['name'], 'Device name cannot be an empty string')
        
        # Check the amount of devices in the database is the same as in the beginning
        self.assertEqual(Device.objects.count(), 4)
        
    
    def test_good_device_delete(self):
        # Check the initial amount of devices in the database
        self.assertEqual(Device.objects.count(), 4)
        
        mac_address = 'aa:aa:aa:aa:aa:aa'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Issue a DELETE request
        response = self.client.delete('/api/v2/device/' + mac_address + '/')
        
        # Check that the response is 204 No Content
        self.assertEqual(response.status_code, 204)
        
        # Check that the device does not exist in the database anymore
        self.assertFalse(Device.objects.filter(mac_address=mac_address).exists())
        
        # Check the final amount of devices in the database
        self.assertEqual(Device.objects.count(), 3)
    
    
    def test_bad_device_deletes(self):
        # Check the initial amount of devices in the database
        self.assertEqual(Device.objects.count(), 4)
        
        # Ensure that the deletion of a non-existent device throws 404 Not Found
        mac_address = 'ff:ff:ff:ff:ff:ff'
        self.assertFalse(Device.objects.filter(mac_address=mac_address).exists())
        response = self.client.delete('/api/v2/device/' + mac_address + '/')
        self.assertEqual(response.status_code, 404)
        
        
        # The deletion of all devices should throw 405 Method Not Allowed
        response = self.client.delete('/api/v2/device/')
        self.assertEqual(response.status_code, 405)
        
        
        # Check the amount of devices in the database is the same as in the beginning
        self.assertEqual(Device.objects.count(), 4)
    
    def test_good_device_get_list(self):
        # Check the initial amount of devices in the database
        self.assertEqual(Device.objects.count(), 4)
        
        # Get a list of devices including their information
        response = self.client.get('/api/v2/device/')
        
        # Check that the response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Convert the json to python
        content = json.loads(response.content)
        
        # Check that all the devices are in the list
        self.assertEqual([device['mac_address'] for device in content['objects']], ['aa:aa:aa:aa:aa:aa', 'bb:bb:bb:bb:bb:bb', 'cc:cc:cc:cc:cc:cc', 'dd:dd:dd:dd:dd:dd'])
        
        # Check that the number of devices in the list is 4
        # (the amount of devices in the fixture)
        self.assertEqual(len(content['objects']), 4)
        
    def test_good_device_get_detail(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Get the information related to one device
        response = self.client.get('/api/v2/device/' + mac_address + '/')
        
        # Check that the response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that the values are correct
        content = json.loads(response.content)
        self.assertEqual(content['created_at'], '2011-12-19T16:21:43.834112')
        self.assertFalse(content['is_reserved'])
        self.assertEqual(content['mac_address'], 'aa:aa:aa:aa:aa:aa')
        self.assertEqual(content['name'], 'Device one')
        self.assertEqual(content['proximity_devices'], [])
        self.assertEqual(content['resource_uri'], '/api/v2/device/aa:aa:aa:aa:aa:aa/')
        self.assertEqual(content['updated_at'], '2011-12-20T12:49:03.998318')
        
    
    def test_bad_device_get_details(self):
        mac_address = 'ff:ff:ff:ff:ff:ff'
        
        # Check that the device does not exist in the database
        self.assertFalse(Device.objects.filter(mac_address=mac_address).exists())
        
        # Issue a get request on a non-existent device
        response = self.client.get('/api/v2/device/' + mac_address + '/')
        
        # Check that the response code is 404 Not Found
        self.assertEqual(response.status_code, 404)
    
    def test_good_device_updates(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Send a put request to update is_reserved to True
        response = self.client.get('/api/v2/device/' + mac_address + '/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse(content['is_reserved'])
        payload = json.dumps({'is_reserved': True})
        response = self.client.put('/api/v2/device/' + mac_address + '/', payload, 'application/json')
        self.assertEqual(response.status_code, 204)
        response = self.client.get('/api/v2/device/' + mac_address + '/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content['is_reserved'])
        
        
        # Send a put request to update the device name
        response = self.client.get('/api/v2/device/' + mac_address + '/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['name'], 'Device one')
        payload = json.dumps({'name': 'Test device'})
        response = self.client.put('/api/v2/device/' + mac_address + '/', payload, 'application/json')
        self.assertEqual(response.status_code, 204)
        response = self.client.get('/api/v2/device/' + mac_address + '/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['name'], 'Test device')
        
        
        # TODO: update proximity devices
    
    def test_bad_device_updates(self):
        mac_address = 'aa:aa:aa:aa:aa:aa'
        
        # Check that the device actually exists in the database
        self.assertTrue(Device.objects.filter(mac_address=mac_address).exists())
        
        # Send a put request to update the device mac address
        payload = json.dumps({'mac_address': 'aa:bb:cc:dd:ee:ff'})
        response = self.client.put('/api/v2/device/' + mac_address + '/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['mac_address'], 'Mac address cannot be updated')
        
        
        # Send a put request to update the created_at field
        payload = json.dumps({'created_at': '2011-12-22T16:21:43.834112'})
        response = self.client.put('/api/v2/device/' + mac_address + '/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['created_at'], 'Created at cannot be updated')
        
        
        # Send a put request to update the updated_at field
        payload = json.dumps({'updated_at': '2011-12-22T16:21:43.834112'})
        response = self.client.put('/api/v2/device/' + mac_address + '/', payload, 'application/json')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['updated_at'], 'Updated at cannot be updated')
        
        
        # Send a put request to update a non-existent device
        payload = json.dumps({'is_reserved': True})
        response = self.client.put('/api/v2/device/aa:bb:cc:dd:ee:ff/', payload, 'application/json')
        self.assertEqual(response.status_code, 404)

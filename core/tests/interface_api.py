from core.clients import ProximityClient
from core.models import Interface
from django.conf import settings
from django.test import TestCase
import json

class InterfaceAPITestCase(TestCase):
    fixtures = ['interfaces_testdata']
    
    def setUp(self):
        self.old_setting = settings.PROXIMITY_SERVER['default']
        settings.PROXIMITY_SERVER['default'] = settings.PROXIMITY_SERVER['test']
        self.proximity_client = ProximityClient()
        self.proximity_client.flush()
        
    def tearDown(self):
        settings.PROXIMITY_SERVER['default'] = self.old_setting
    
    def test_bad_interface_post(self):
        # Check the initial amount of interfaces in the database
        self.assertEqual(Interface.objects.count(), 2)
        
        # The interface data
        payload = json.dumps({'name': 'SingingDevice'})
        
        # Issue a POST request
        response = self.client.post('/api/v2/interface/', payload, 'application/json')
        
        # Check that the response is 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)
        
        # Check the amount of interfaces in the database is the same as in the beginning
        self.assertEqual(Interface.objects.count(), 2)
        
    def test_bad_interface_delete(self):
        # Check the initial amount of interfaces in the database
        self.assertEqual(Interface.objects.count(), 2)
        
        # The deletion of all devices should throw 405 Method Not Allowed
        response = self.client.delete('/api/v2/interface/')
        self.assertEqual(response.status_code, 405)
        
        # The deletion of an interface should throw 405 Method Not Allowed
        name = 'TalkingDevice'
        response = self.client.delete('/api/v2/interface/' + name + '/')
        self.assertEqual(response.status_code, 405)
        
        # Check the amount of interfaces in the database is the same as in the beginning
        self.assertEqual(Interface.objects.count(), 2)
    
    def test_good_interface_get_list(self):
        # Check the initial amount of interfaces in the database
        self.assertEqual(Interface.objects.count(), 2)
        
        # Get a list of interfaces including their information
        response = self.client.get('/api/v2/interface/')
        
        # Check that the response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Convert the json to python
        content = json.loads(response.content)
        
        # Check that all the interfaces are in the list
        self.assertEqual([interface['name'] for interface in content['objects']], ['TalkingDevice', 'CalendarSource'])
        
        # Check that the number of interfaces in the list is 2
        self.assertEqual(len(content['objects']), 2)
    
    def test_good_interface_get_detail(self):
        name = 'TalkingDevice'
        
        # Check that the interface actually exists in the database
        self.assertTrue(Interface.objects.filter(name=name).exists())
        
        # Get the information related to one interface
        response = self.client.get('/api/v2/interface/' + name + '/')
        
        # Check that the response code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that the values are correct
        content = json.loads(response.content)
        self.assertEqual(content['created_at'], '2011-12-22T16:21:43.834112')
        self.assertEqual(content['name'], 'TalkingDevice')
        self.assertEqual(content['resource_uri'], '/api/v2/interface/TalkingDevice/')
        self.assertEqual(content['updated_at'], '2011-12-22T23:49:03.998318')
    
    def test_bad_interface_get_details(self):
        name = 'SingingDevice'
        
        # Check that the device does not exist in the database
        self.assertFalse(Interface.objects.filter(name=name).exists())
        
        # Issue a get request on a non-existent interface
        response = self.client.get('/api/v2/interface/' + name + '/')
        
        # Check that the response code is 404 Not Found
        self.assertEqual(response.status_code, 404)
    
    def test_bad_interface_update(self):
        name = 'TalkingDevice'
        
        # Check that the device actually exists in the database
        self.assertTrue(Interface.objects.filter(name=name).exists())
        
        # The interface data to be updated
        payload = json.dumps({'name': 'SingingDevice'})
        
        # Issue a PUT request in order to update the interface
        response = self.client.put('/api/v2/interface/' + name + '/', payload, 'application/json')
        
        # Check that the response is 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)
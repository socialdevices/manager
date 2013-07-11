from core.clients import ProximityClient
from core.models import Interface, Method, Trigger, MethodParameter
from django.conf import settings
from django.test.testcases import TestCase
from mock import patch
import json

# Patch the MirriClient used by forms with a mock object in every test
@patch('core.forms.MirriClient', spec_set=True)
class InterfaceFileAPITestCase(TestCase):
    fixtures = ['interface_file_api_testdata']
    
    def setUp(self):
        self.old_setting = settings.PROXIMITY_SERVER['default']
        settings.PROXIMITY_SERVER['default'] = settings.PROXIMITY_SERVER['test']
        self.proximity_client = ProximityClient()
        self.proximity_client.flush()
        
    def tearDown(self):
        settings.PROXIMITY_SERVER['default'] = self.old_setting
    
    def test_good_upload(self, MirriMockClass):
        # Check the initial amount of interfaces in the database
        self.assertEqual(Interface.objects.count(), 1)
        
        # Check the initial amount of methods in the database
        self.assertEqual(Method.objects.count(), 2)
        
        # Check the initial amount of method parameters in the database
        self.assertEqual(MethodParameter.objects.count(), 0)
        
        # Check the initial amount of triggers in the database
        self.assertEqual(Trigger.objects.count(), 0)
        
        # TalkingDevice
        f = open('core/fixtures/talkingDevices/talkingDevice.py')
        response = self.client.post('/api/interface_file/', {'file': f})
        f.seek(0)
        interface_code = f.read()
        f.close()
        
        self.assertEqual(response.status_code, 201)
        
        self.assertTrue(Interface.objects.filter(name='TalkingDevice').exists())
        self.assertTrue(Method.objects.filter(interface__name='TalkingDevice', name='isWilling').exists())
        self.assertTrue(Method.objects.filter(interface__name='TalkingDevice', name='isSilent').exists())
        self.assertTrue(Trigger.objects.filter(method__interface__name='TalkingDevice', method__name='isSilent').exists())
        
        # Check that the file was uploaded to Mirri
        mirri_mock = MirriMockClass.return_value
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 1)
        self.assertEqual(len(mirri_mock.upload_interface_file.call_args[0]), 2)
        self.assertEqual(mirri_mock.upload_interface_file.call_args[0][0], 'TalkingDevice')
        mirri_mock.upload_interface_file.call_args[0][1].seek(0)
        self.assertEqual(mirri_mock.upload_interface_file.call_args[0][1].read(), interface_code)
        
        
        # CalendarSource
        mirri_mock.reset_mock()
        f = open('core/fixtures/calendarReminders/calendarSource.py')
        response = self.client.post('/api/interface_file/', {'file': f})
        f.seek(0)
        interface_code = f.read()
        f.close()
        
        self.assertEqual(response.status_code, 201)
        
        self.assertTrue(Interface.objects.filter(name='CalendarSource').exists())
        self.assertTrue(Method.objects.filter(interface__name='CalendarSource', name='eventApproaching').exists())
        self.assertTrue(MethodParameter.objects.filter(method__interface__name='CalendarSource', method__name='eventApproaching', name='eid').exists())
        self.assertTrue(Trigger.objects.filter(method__interface__name='CalendarSource', method__name='eventApproaching').exists())
        
        # Check that the file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 1)
        self.assertEqual(len(mirri_mock.upload_interface_file.call_args[0]), 2)
        self.assertEqual(mirri_mock.upload_interface_file.call_args[0][0], 'CalendarSource')
        mirri_mock.upload_interface_file.call_args[0][1].seek(0)
        self.assertEqual(mirri_mock.upload_interface_file.call_args[0][1].read(), interface_code)
        
        
        # Check the final amount of interfaces in the database
        self.assertEqual(Interface.objects.count(), 3)
        
        # Check the final amount of methods in the database
        self.assertEqual(Method.objects.count(), 5)
        
        # Check the final amount of method parameters in the database
        self.assertEqual(MethodParameter.objects.count(), 1)
        
        # Check the final amount of triggers in the database
        self.assertEqual(Trigger.objects.count(), 2)
    
    
    def test_bad_upload(self, MirriMockClass):
        # Check the initial amount of interfaces in the database
        self.assertEqual(Interface.objects.count(), 1)
        
        # Check the initial amount of methods in the database
        self.assertEqual(Method.objects.count(), 2)
        
        # Check the initial amount of method parameters in the database
        self.assertEqual(MethodParameter.objects.count(), 0)
        
        # Check the initial amount of triggers in the database
        self.assertEqual(Trigger.objects.count(), 0)
        
        
        # A syntax error in the interface file
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevice_syntax_error.py')
        response = self.client.post('/api/interface_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['File talkingDevice_syntax_error.py contains syntax errors (line 15, col 22): class TalkingDevice()\n'])
        
        # Check that no file was uploaded to Mirri
        mirri_mock = MirriMockClass.return_value
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The interface file does not contain any interfaces
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevice_no_interface.py')
        response = self.client.post('/api/interface_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Interface parse error in file talkingDevice_no_interface.py: Interface decorator @deviceInterface is missing.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The interface file does not contain any precondition methods
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevice_no_precondition_methods.py')
        response = self.client.post('/api/interface_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Interface parse error in file talkingDevice_no_precondition_methods.py: Interface TalkingDevice does not have any precondition methods defined with decorator @precondition.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The interface file does not contain any triggers
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevice_no_triggers.py')
        response = self.client.post('/api/interface_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Interface parse error in file talkingDevice_no_triggers.py: No trigger method class with base class TriggeringEvent has been defined.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # A trigger in the interface file does not match any of the interface precondition methods
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevice_no_trigger_match.py')
        response = self.client.post('/api/interface_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Interface parse error in file talkingDevice_no_trigger_match.py: The name of the trigger method class IsFree does not match any of the precondition methods defined in interface TalkingDevice.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The interface file contains multiple interfaces
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevice_multiple_interfaces.py')
        response = self.client.post('/api/interface_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Interface parse error in file talkingDevice_multiple_interfaces.py: Multiple interface classes with decorator @deviceInterface have been defined.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The interface file contains a duplicate precondition method
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevice_duplicate_precondition_method.py')
        response = self.client.post('/api/interface_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Interface parse error in file talkingDevice_duplicate_precondition_method.py: Duplicate precondition method isWilling.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The interface file contains a duplicate trigger
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevice_duplicate_trigger.py')
        response = self.client.post('/api/interface_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Interface parse error in file talkingDevice_duplicate_trigger.py: Duplicate trigger method class IsSilent.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The interface file contains a duplicate method parameter
        mirri_mock.reset_mock()
        f = open('core/fixtures/calendarReminders/invalid_files/calendarSource_duplicate_method_parameter.py')
        response = self.client.post('/api/interface_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Interface parse error in file calendarSource_duplicate_method_parameter.py: Duplicate parameter eid for precondition method eventApproaching in interface CalendarSource.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The interface in the interface file already exists
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevice_interface_exists.py')
        response = self.client.post('/api/interface_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Interface TalkingDeviceTest already exists.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # Check the final amount of interfaces in the database
        self.assertEqual(Interface.objects.count(), 1)
        
        # Check the final amount of methods in the database
        self.assertEqual(Method.objects.count(), 2)
        
        # Check the final amount of method parameters in the database
        self.assertEqual(MethodParameter.objects.count(), 0)
        
        # Check the final amount of triggers in the database
        self.assertEqual(Trigger.objects.count(), 0)
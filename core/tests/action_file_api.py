from core.clients import ProximityClient
from core.models import Action, ActionDevice, ActionDeviceInterface, \
    ActionPreconditionMethod
from django.conf import settings
from django.test.testcases import TestCase
from mock import patch
import json

# Patch the MirriClient used by forms with a mock object in every test
@patch('core.forms.MirriClient', spec_set=True)
class ActionFileAPITestCase(TestCase):
    fixtures = ['action_file_api_testdata']
    
    def setUp(self):
        self.old_setting = settings.PROXIMITY_SERVER['default']
        settings.PROXIMITY_SERVER['default'] = settings.PROXIMITY_SERVER['test']
        self.proximity_client = ProximityClient()
        self.proximity_client.flush()
        
    def tearDown(self):
        settings.PROXIMITY_SERVER['default'] = self.old_setting
    
    def test_good_upload(self, MirriMockClass):
        # Check the initial amount of actions in the database
        self.assertEqual(Action.objects.count(), 1)
        
        # Check the initial amount of action devices in the database
        self.assertEqual(ActionDevice.objects.count(), 2)
        
        # Check the initial amount of action device interfaces in the database
        self.assertEqual(ActionDeviceInterface.objects.count(), 2)
        
        # Check the initial amount of action precondition methods in the database
        self.assertEqual(ActionPreconditionMethod.objects.count(), 3)
        
        
        # TalkingDevice - Dialog
        f = open('core/fixtures/talkingDevices/dialog.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.seek(0)
        action_code = f.read()
        f.close()
        
        self.assertEqual(response.status_code, 201)
        
        self.assertTrue(Action.objects.filter(name='Dialog', precondition_expression='(? and ? and ?)').exists())
        self.assertTrue(ActionDevice.objects.filter(action__name='Dialog', name='d1', parameter_position=0).exists())
        self.assertTrue(ActionDevice.objects.filter(action__name='Dialog', name='d2', parameter_position=1).exists())
        self.assertTrue(ActionDeviceInterface.objects.filter(action_device__action__name='Dialog', action_device__name='d1', interface__name='TalkingDevice').exists())
        self.assertTrue(ActionDeviceInterface.objects.filter(action_device__action__name='Dialog', action_device__name='d2', interface__name='TalkingDevice').exists())
        self.assertTrue(ActionPreconditionMethod.objects.filter(expression_position=0, action__name='Dialog', action_device__name='d1', method__name='isWilling').exists())
        self.assertTrue(ActionPreconditionMethod.objects.filter(expression_position=1, action__name='Dialog', action_device__name='d2', method__name='isWilling').exists())
        self.assertTrue(ActionPreconditionMethod.objects.filter(expression_position=2, action__name='Dialog', action_device__name='d1', method__name='isSilent').exists())
        
        # Check that the file was uploaded to Mirri
        mirri_mock = MirriMockClass.return_value
        self.assertEqual(mirri_mock.upload_action_file.call_count, 1)
        self.assertEqual(len(mirri_mock.upload_action_file.call_args[0]), 1)
        mirri_mock.upload_action_file.call_args[0][0].seek(0)
        self.assertEqual(mirri_mock.upload_action_file.call_args[0][0].read(), action_code)
        
        
        # TalkingDevice - ConversationOfThree
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/conversationOfThree.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.seek(0)
        action_code = f.read()
        f.close()
        
        self.assertEqual(response.status_code, 201)
        
        self.assertTrue(Action.objects.filter(name='ConversationOfThree', precondition_expression='(? and ? and ? and ?)').exists())
        self.assertTrue(ActionDevice.objects.filter(action__name='ConversationOfThree', name='d1', parameter_position=0).exists())
        self.assertTrue(ActionDevice.objects.filter(action__name='ConversationOfThree', name='d2', parameter_position=1).exists())
        self.assertTrue(ActionDevice.objects.filter(action__name='ConversationOfThree', name='d3', parameter_position=2).exists())
        self.assertTrue(ActionDeviceInterface.objects.filter(action_device__action__name='ConversationOfThree', action_device__name='d1', interface__name='TalkingDevice').exists())
        self.assertTrue(ActionDeviceInterface.objects.filter(action_device__action__name='ConversationOfThree', action_device__name='d2', interface__name='TalkingDevice').exists())
        self.assertTrue(ActionDeviceInterface.objects.filter(action_device__action__name='ConversationOfThree', action_device__name='d3', interface__name='TalkingDevice').exists())
        self.assertTrue(ActionPreconditionMethod.objects.filter(expression_position=0, action__name='ConversationOfThree', action_device__name='d1', method__name='isWilling').exists())
        self.assertTrue(ActionPreconditionMethod.objects.filter(expression_position=1, action__name='ConversationOfThree', action_device__name='d2', method__name='isWilling').exists())
        self.assertTrue(ActionPreconditionMethod.objects.filter(expression_position=2, action__name='ConversationOfThree', action_device__name='d3', method__name='isWilling').exists())
        self.assertTrue(ActionPreconditionMethod.objects.filter(expression_position=3, action__name='ConversationOfThree', action_device__name='d1', method__name='isSilent').exists())
        
        # Check that the file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_action_file.call_count, 1)
        self.assertEqual(len(mirri_mock.upload_action_file.call_args[0]), 1)
        mirri_mock.upload_action_file.call_args[0][0].seek(0)
        self.assertEqual(mirri_mock.upload_action_file.call_args[0][0].read(), action_code)
        
        
        # CalendarSource - Conversation
        mirri_mock.reset_mock()
        f = open('core/fixtures/calendarReminders/conversation.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.seek(0)
        action_code = f.read()
        f.close()
        
        self.assertEqual(response.status_code, 201)
        
        self.assertTrue(Action.objects.filter(name='Conversation', precondition_expression='(?)').exists())
        self.assertTrue(ActionDevice.objects.filter(action__name='Conversation', name='source', parameter_position=0).exists())
        self.assertTrue(ActionDevice.objects.filter(action__name='Conversation', name='d2', parameter_position=1).exists())
        self.assertTrue(ActionDevice.objects.filter(action__name='Conversation', name='d3', parameter_position=2).exists())
        self.assertTrue(ActionDeviceInterface.objects.filter(action_device__action__name='Conversation', action_device__name='source', interface__name='TalkingDevice').exists())
        self.assertTrue(ActionDeviceInterface.objects.filter(action_device__action__name='Conversation', action_device__name='source', interface__name='CalendarSource').exists())
        self.assertTrue(ActionDeviceInterface.objects.filter(action_device__action__name='Conversation', action_device__name='d2', interface__name='TalkingDevice').exists())
        self.assertTrue(ActionDeviceInterface.objects.filter(action_device__action__name='Conversation', action_device__name='d3', interface__name='TalkingDevice').exists())
        self.assertTrue(ActionPreconditionMethod.objects.filter(expression_position=0, action__name='Conversation', action_device__name='source', method__name='eventApproaching').exists())
        
        # Check that the file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_action_file.call_count, 1)
        self.assertEqual(len(mirri_mock.upload_action_file.call_args[0]), 1)
        mirri_mock.upload_action_file.call_args[0][0].seek(0)
        self.assertEqual(mirri_mock.upload_action_file.call_args[0][0].read(), action_code)
        
        
        # CalendarSource - FakeCall
        mirri_mock.reset_mock()
        f = open('core/fixtures/calendarReminders/fakeCall.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.seek(0)
        action_code = f.read()
        f.close()
        
        self.assertEqual(response.status_code, 201)
        
        self.assertTrue(Action.objects.filter(name='FakeCall', precondition_expression='(?)').exists())
        self.assertTrue(ActionDevice.objects.filter(action__name='FakeCall', name='d1', parameter_position=0).exists())
        self.assertTrue(ActionDevice.objects.filter(action__name='FakeCall', name='d2', parameter_position=1).exists())
        self.assertTrue(ActionDeviceInterface.objects.filter(action_device__action__name='FakeCall', action_device__name='d1', interface__name='TalkingDevice').exists())
        self.assertTrue(ActionDeviceInterface.objects.filter(action_device__action__name='FakeCall', action_device__name='d1', interface__name='CalendarSource').exists())
        self.assertTrue(ActionDeviceInterface.objects.filter(action_device__action__name='FakeCall', action_device__name='d2', interface__name='TalkingDevice').exists())
        self.assertTrue(ActionPreconditionMethod.objects.filter(expression_position=0, action__name='FakeCall', action_device__name='d1', method__name='eventApproaching').exists())
        
        # Check that the file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_action_file.call_count, 1)
        self.assertEqual(len(mirri_mock.upload_action_file.call_args[0]), 1)
        mirri_mock.upload_action_file.call_args[0][0].seek(0)
        self.assertEqual(mirri_mock.upload_action_file.call_args[0][0].read(), action_code)
        
        
        # Check the final amount of actions in the database
        self.assertEqual(Action.objects.count(), 5)
        
        # Check the final amount of action devices in the database
        self.assertEqual(ActionDevice.objects.count(), 12)
        
        # Check the final amount of action device interfaces in the database
        self.assertEqual(ActionDeviceInterface.objects.count(), 14)
        
        # Check the final amount of action precondition methods in the database
        self.assertEqual(ActionPreconditionMethod.objects.count(), 12)
        
        
    def test_bad_upload(self, MirriMockClass):
        # Check the initial amount of actions in the database
        self.assertEqual(Action.objects.count(), 1)
        
        # Check the initial amount of action devices in the database
        self.assertEqual(ActionDevice.objects.count(), 2)
        
        # Check the initial amount of action device interfaces in the database
        self.assertEqual(ActionDeviceInterface.objects.count(), 2)
        
        # Check the initial amount of action precondition methods in the database
        self.assertEqual(ActionPreconditionMethod.objects.count(), 3)
        
        
        # A syntax error in the action file
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_syntax_error.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['File dialog_syntax_error.py contains syntax errors (line 13, col 21): class Dialog(Action)\n'])
        
        # Check that no file was uploaded to Mirri
        mirri_mock = MirriMockClass.return_value
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The action file does not contain any actions
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_no_action.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_no_action.py: No action class with base class Action has been defined.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The action file does not contain an action precondition
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_no_action_precondition.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_no_action_precondition.py: No method with decorator @actionprecondition has been defined for action class Dialog.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The action precondition does not have any parameters
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_no_action_precondition_parameters.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_no_action_precondition_parameters.py: Precondition method precondition does not have any parameters.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The action precondition does not have a return statement
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_no_action_precondition_return.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_no_action_precondition_return.py: The precondition method precondition does not have a return statement.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The return statement in the action precondition does not contain a boolean expression
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_no_boolean_in_return.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_no_boolean_in_return.py: The return statement in the precondition method does not contain a boolean expression.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # No interfaces have been declared for the devices in the action precondition
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_no_action_device_interfaces.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_no_action_device_interfaces.py: Method hasInterface() has not been called in the return statement of the precondition method.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The return statement does not contain a valid boolean precondition expression
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_no_precondition_expression.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_no_precondition_expression.py: The return statement of the precondition method in class Dialog does not contain a valid boolean precondition expression consisting of precondition methods.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # An action device is not declared in the precondition parameters
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_no_device_parameter.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_no_device_parameter.py: Device d1 is not declared in the precondition parameters.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # A precondition method call is incorrect in the action precondition
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_precondition_method_call_error.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_precondition_method_call_error.py: The format of the precondition method call is incorrect (line 21, col 44): isWilling. The format should be <device>.<interface>.<precondition_method>.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # A device has not been declared any interfaces
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_device_without_interfaces.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_device_without_interfaces.py: No interfaces have been declared for device d1 with method hasInterface().'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # A device has not been declared any interfaces
        mirri_mock.reset_mock()
        f = open('core/fixtures/calendarReminders/invalid_files/conversation_device_interface_missing.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file conversation_device_interface_missing.py: Interface TalkingDevice has not been declared for device source with method hasInterface().'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The return statement in the action precondition contains a value other than 
        # a function call or a boolean expression
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_invalid_return.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_invalid_return.py: The boolean expression in the return statement of the action precondition method can only consist of function calls or nested boolean expressions.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The action file contains multiple actions
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_multiple_actions.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_multiple_actions.py: Multiple action classes with base class Action have been defined.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # The action precondition contains a duplicate parameter
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_duplicate_precondition_parameter.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_duplicate_precondition_parameter.py: Duplicate parameter d1 for precondition method precondition.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # A device has a duplicate interface
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_duplicate_device_interface.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action parse error in file dialog_duplicate_device_interface.py: Method hasInterface(\'TalkingDevice\') called multiple times for action device d1.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # An action already exists
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_action_exists.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action DialogTest already exists.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # A non-existent interface
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_non_existent_interface.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Interface TalkingDeviceTest does not exist.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        # A non-existent method
        mirri_mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/dialog_non_existent_method.py')
        response = self.client.post('/api/action_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Method isWillingTest does not exist for interface TalkingDevice.'])
        
        # Check that no file was uploaded to Mirri
        self.assertEqual(mirri_mock.upload_interface_file.call_count, 0)
        
        
        
        # Check the final amount of actions in the database
        self.assertEqual(Action.objects.count(), 1)
        
        # Check the final amount of action devices in the database
        self.assertEqual(ActionDevice.objects.count(), 2)
        
        # Check the final amount of action device interfaces in the database
        self.assertEqual(ActionDeviceInterface.objects.count(), 2)
        
        # Check the final amount of action precondition methods in the database
        self.assertEqual(ActionPreconditionMethod.objects.count(), 3)
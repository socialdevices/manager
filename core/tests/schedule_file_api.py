from core.clients import ProximityClient
from core.models import Schedule, ScheduleAction
from django.conf import settings
from django.test.testcases import TestCase
from mock import patch
import json

# Patch the GenerateConfigurationModelThread with a mock object in every test
@patch('core.signals.GenerateConfigurationModelThread', spec_set=True)
class ScheduleFileAPITestCase(TestCase):
    fixtures = ['schedule_file_api_testdata']
    
    def setUp(self):
        self.old_setting = settings.PROXIMITY_SERVER['default']
        settings.PROXIMITY_SERVER['default'] = settings.PROXIMITY_SERVER['test']
        self.proximity_client = ProximityClient()
        self.proximity_client.flush()
        
    def tearDown(self):
        settings.PROXIMITY_SERVER['default'] = self.old_setting
    
    def test_good_upload(self, MockClass):
        # Check the initial amount of schedules in the database
        self.assertEqual(Schedule.objects.count(), 1)
        
        # Check the initial amount of schedule actions in the database
        self.assertEqual(ScheduleAction.objects.count(), 2)
        
        
        # talkingDevicesSCH
        f = open('core/fixtures/talkingDevices/talkingDevicesSCH.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 201)
        
        self.assertTrue(Schedule.objects.filter(name='talkingDevicesSCH', trigger__method__interface__name='TalkingDevice', trigger__method__name='isSilent').exists())
        self.assertTrue(ScheduleAction.objects.filter(schedule__name='talkingDevicesSCH', action__name='Dialog', trigger_device__action__name='Dialog', trigger_device__parameter_position=0).exists())
        self.assertTrue(ScheduleAction.objects.filter(schedule__name='talkingDevicesSCH', action__name='ConversationOfThree', trigger_device__action__name='ConversationOfThree', trigger_device__parameter_position=0).exists())
        
        # Check that the upload of the schedule file triggered a signal
        # to generate the configuration model in a thread
        self.assertEqual(MockClass.call_count, 1)
        self.assertEqual(MockClass.call_args[0][0].name, 'talkingDevicesSCH')
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 1)
        
        
        # calendarReminderSCH
        MockClass.reset_mock()
        mock.reset_mock()
        f = open('core/fixtures/calendarReminders/calendarReminderSCH.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 201)
        
        self.assertTrue(Schedule.objects.filter(name='calendarReminder', trigger__method__interface__name='CalendarSource', trigger__method__name='eventApproaching').exists())
        self.assertTrue(ScheduleAction.objects.filter(schedule__name='calendarReminder', action__name='Conversation', trigger_device__action__name='Conversation', trigger_device__parameter_position=0).exists())
        self.assertTrue(ScheduleAction.objects.filter(schedule__name='calendarReminder', action__name='FakeCall', trigger_device__action__name='FakeCall', trigger_device__parameter_position=0).exists())
        
        # Check that the upload of the schedule file triggered a signal
        # to generate the configuration model in a thread
        self.assertEqual(MockClass.call_count, 1)
        self.assertEqual(MockClass.call_args[0][0].name, 'calendarReminder')
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 1)
        
        
        # Check the final amount of schedules in the database
        self.assertEqual(Schedule.objects.count(), 3)
        
        # Check the final amount of schedule actions in the database
        self.assertEqual(ScheduleAction.objects.count(), 6)
    
    def test_bad_upload(self, MockClass):
        # Check the initial amount of schedules in the database
        self.assertEqual(Schedule.objects.count(), 1)
        
        # Check the initial amount of schedule actions in the database
        self.assertEqual(ScheduleAction.objects.count(), 2)
        
        
        # A syntax error in the schedule file
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevicesSCH_syntax_error.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['File talkingDevicesSCH_syntax_error.py contains syntax errors (line 16, col 39): def talkingDevicesSCH(triggeringEvent)\n'])
        
        # Check that the configuration model generator thread is not started
        self.assertEqual(MockClass.call_count, 0)
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 0)
        
        
        # The schedule file does not contain any schedules
        MockClass.reset_mock()
        mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevicesSCH_no_schedule.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Schedule parse error in file talkingDevicesSCH_no_schedule.py: No schedule function with decorator @schedulingFunction has been defined.'])
        
        # Check that the configuration model generator thread is not started
        self.assertEqual(MockClass.call_count, 0)
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 0)
        
        
        # The schedule file does not contain any schedule actions
        MockClass.reset_mock()
        mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevicesSCH_no_schedule_actions.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Schedule parse error in file talkingDevicesSCH_no_schedule_actions.py: The schedule function does not contain any actions.'])
        
        # Check that the configuration model generator thread is not started
        self.assertEqual(MockClass.call_count, 0)
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 0)
        
        
        # The schedule file does not contain a trigger method for the schedule
        MockClass.reset_mock()
        mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevicesSCH_no_trigger.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Schedule parse error in file talkingDevicesSCH_no_trigger.py: No trigger method defined for the schedule with scheduling.addSchedule() in __main__.'])
        
        # Check that the configuration model generator thread is not started
        self.assertEqual(MockClass.call_count, 0)
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 0)
        
        
        # The schedule file does not contain an interface for the trigger method of the schedule
        MockClass.reset_mock()
        mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevicesSCH_no_trigger_interface.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Schedule parse error in file talkingDevicesSCH_no_trigger_interface.py: The trigger method has not been imported from an interface module.'])
        
        # Check that the configuration model generator thread is not started
        self.assertEqual(MockClass.call_count, 0)
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 0)
        
        
        # The schedule function does not have a return statement
        MockClass.reset_mock()
        mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevicesSCH_no_return.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Schedule parse error in file talkingDevicesSCH_no_return.py: The schedule function talkingDevicesSCH does not have a return statement.'])
        
        # Check that the configuration model generator thread is not started
        self.assertEqual(MockClass.call_count, 0)
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 0)
        
        
        # The return statement of the schedule function does not contain a list
        MockClass.reset_mock()
        mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevicesSCH_no_return_list.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Schedule parse error in file talkingDevicesSCH_no_return_list.py: The return statement of the schedule function does not contain a list.'])
        
        # Check that the configuration model generator thread is not started
        self.assertEqual(MockClass.call_count, 0)
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 0)
        
        
        # The return statement of the schedule function does not contain a list of variables
        MockClass.reset_mock()
        mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevicesSCH_no_return_list_variables.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Schedule parse error in file talkingDevicesSCH_no_return_list_variables.py: The list in the return statement of the schedule function does not have variable names as list members.'])
        
        # Check that the configuration model generator thread is not started
        self.assertEqual(MockClass.call_count, 0)
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 0)
        
        
        # The schedule contains a duplicate action
        MockClass.reset_mock()
        mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevicesSCH_duplicate_action.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Schedule parse error in file talkingDevicesSCH_duplicate_action.py: Duplicate schedule action Dialog.'])
        
        # Check that the configuration model generator thread is not started
        self.assertEqual(MockClass.call_count, 0)
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 0)
        
        
        # A schedule already exists
        MockClass.reset_mock()
        mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevicesSCH_schedule_exists.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Schedule talkingDevicesSCHTest already exists.'])
        
        # Check that the configuration model generator thread is not started
        self.assertEqual(MockClass.call_count, 0)
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 0)
        
        
        # Trigger method does not exist
        MockClass.reset_mock()
        mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevicesSCH_non_existent_trigger.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Trigger method isSilentTest does not exist for interface TalkingDevice.'])
        
        # Check that the configuration model generator thread is not started
        self.assertEqual(MockClass.call_count, 0)
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 0)
        
        
        # Action does not exist
        MockClass.reset_mock()
        mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevicesSCH_non_existent_action.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Action DialogTest does not exist.'])
        
        # Check that the configuration model generator thread is not started
        self.assertEqual(MockClass.call_count, 0)
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 0)
        
        
        # Action device does not exist for a specific trigger from position
        MockClass.reset_mock()
        mock.reset_mock()
        f = open('core/fixtures/talkingDevices/invalid_files/talkingDevicesSCH_non_existent_action_device.py')
        response = self.client.post('/api/schedule_file/', {'file': f})
        f.close()
        
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['file'], ['Trigger from position 2 does not correspond to any valid action device position in action Dialog.'])
        
        # Check that the configuration model generator thread is not started
        self.assertEqual(MockClass.call_count, 0)
        mock = MockClass.return_value
        self.assertEqual(mock.start.call_count, 0)
        
        
        
        # Check the final amount of schedules in the database
        self.assertEqual(Schedule.objects.count(), 1)
        
        # Check the final amount of schedule actions in the database
        self.assertEqual(ScheduleAction.objects.count(), 2)
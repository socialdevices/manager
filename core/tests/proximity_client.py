from core.clients import ProximityClient
from django.conf import settings
from django.test import TestCase

class ProximityClientTestCase(TestCase):

    def setUp(self):
        self.old_setting = settings.PROXIMITY_SERVER['default']
        settings.PROXIMITY_SERVER['default'] = settings.PROXIMITY_SERVER['test']
        self.proximity_client = ProximityClient()
        self.proximity_client.flush()

    def tearDown(self):
        settings.PROXIMITY_SERVER['default'] = self.old_setting
    
    def test_good_add_set_get_flush(self):
        self.proximity_client.add_device('aa:aa:aa:aa:aa:aa')
        group = self.proximity_client.get_group('aa:aa:aa:aa:aa:aa')
        self.assertEqual(group, [])
        
        self.proximity_client.add_device('bb:bb:bb:bb:bb:bb')
        group = self.proximity_client.get_group('aa:aa:aa:aa:aa:aa')
        self.assertEqual(group, [])
        
        self.proximity_client.add_device('cc:cc:cc:cc:cc:cc')
        group = self.proximity_client.get_group('cc:cc:cc:cc:cc:cc')
        self.assertEqual(group, [])
        
        
        self.proximity_client.set_group('aa:aa:aa:aa:aa:aa', ['bb:bb:bb:bb:bb:bb'])
        group = self.proximity_client.get_group('aa:aa:aa:aa:aa:aa')
        self.assertEqual(group, ['bb:bb:bb:bb:bb:bb'])
        group = self.proximity_client.get_group('bb:bb:bb:bb:bb:bb')
        self.assertEqual(group, ['aa:aa:aa:aa:aa:aa'])
        group = self.proximity_client.get_group('cc:cc:cc:cc:cc:cc')
        self.assertEqual(group, [])
        
        self.proximity_client.set_group('cc:cc:cc:cc:cc:cc', ['bb:bb:bb:bb:bb:bb'])
        group = self.proximity_client.get_group('aa:aa:aa:aa:aa:aa')
        self.assertEqual(group, ['bb:bb:bb:bb:bb:bb', 'cc:cc:cc:cc:cc:cc'])
        group = self.proximity_client.get_group('bb:bb:bb:bb:bb:bb')
        self.assertEqual(group, ['aa:aa:aa:aa:aa:aa', 'cc:cc:cc:cc:cc:cc'])
        group = self.proximity_client.get_group('cc:cc:cc:cc:cc:cc')
        self.assertEqual(group, ['aa:aa:aa:aa:aa:aa', 'bb:bb:bb:bb:bb:bb'])
        
        self.proximity_client.flush()
        group = self.proximity_client.get_group('aa:aa:aa:aa:aa:aa')
        self.assertEqual(group, [])
        group = self.proximity_client.get_group('bb:bb:bb:bb:bb:bb')
        self.assertEqual(group, [])
        group = self.proximity_client.get_group('cc:cc:cc:cc:cc:cc')
        self.assertEqual(group, [])
        
import unittest
from alerts import *

class TestAlertFunctionsBase(unittest.TestCase):

    def setUp(self):
        self.test_tenant = 'test'
        self.client = HawkularAlertsClient(user='jdoe', password='password', tenant_id=self.test_tenant)

class AlertsTestCase(TestAlertFunctionsBase):

    def test_status(self):
        resp = self.client.status()
        self.assertTrue(resp.has_key('status'))
        self.assertTrue(resp.has_key('Implementation-Version'))
        self.assertTrue(resp.has_key('Built-From-Git-SHA1'))

if __name__ == '__main__':
    unittest.main()

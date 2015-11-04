import unittest
import ut_config
from rest_client import RestClient
from transcirrus.common import util
import transcirrus.common.version as ver

class VersionTestCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        node_id = util.get_node_id()
        host = util.get_system_variables(node_id)['MGMT_IP']
        cls.rest = RestClient(ut_config.scheme, host, ut_config.port, ut_config.service_path)
        return

    @classmethod
    def tearDownClass(cls):
        return

    def setUp(self):
        return

    def tearDown(self):
        return

    def testGetVersion(self):
        path = "/version"
        data = self.rest.invoke('GET', path)
        version = data['version']
        self.assertEqual(version['major'], ver.VERSION_MAJOR, "version major mismatch")
        self.assertEqual(version['minor'], ver.VERSION_MINOR, "version minor mismatch")
        self.assertEqual(version['release'], ver.VERSION_RELEASE, "version release mismatch")
        self.assertEqual(version['full_str'], ver.VERSION_FULL_STR, "version full_str mismatch")
        self.assertEqual(version['short_str'], ver.VERSION_SHORT_STR, "version short_str mismatch")
        return

if __name__ == "__main__":
    unittest.main(verbosity=2)

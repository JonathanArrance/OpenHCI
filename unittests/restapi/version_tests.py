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
        self.assertEqual(str(version['major']), str(ver.VERSION_MAJOR), "version major mismatch: got %s | excepted %s" % (version['major'], ver.VERSION_MAJOR))
        self.assertEqual(str(version['minor']), str(ver.VERSION_MINOR), "version minor mismatch: got %s | excepted %s" % (version['minor'], ver.VERSION_MINOR))
        self.assertEqual(str(version['release']), str(ver.VERSION_RELEASE), "version release mismatch: got %s | excepted %s" % (version['release'], ver.VERSION_RELEASE))
        self.assertEqual(str(version['full']), str(ver.VERSION_FULL_STR), "version full_str mismatch: got %s | excepted %s" % (version['full'], ver.VERSION_FULL_STR))
        self.assertEqual(str(version['short']), str(ver.VERSION_SHORT_STR), "version short_str mismatch: got %s | excepted %s" % (version['short'], ver.VERSION_SHORT_STR))
        return

if __name__ == "__main__":
    unittest.main(verbosity=2)

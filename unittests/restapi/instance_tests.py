import unittest
import ut_config
from rest_client import RestClient
from transcirrus.common import util
from project import Project
import project as Proj
from instance import Instance
import instance as Inst
from user import User
import user as Usr

class InstanceTestCases(unittest.TestCase):
    # Setup everything we need before we get started. This routine is only called
    # once when the class is created.
    @classmethod
    def setUpClass(cls):
        # Find out mgmt IP address because we have to connect to it for REST calls.
        node_id = util.get_node_id()
        host = util.get_system_variables(node_id)['MGMT_IP']

        # Configure the rest client and project classes.
        cls.rest = RestClient(ut_config.scheme, host, ut_config.port, ut_config.service_path)
        cls.project = Project()
        cls.instance = Instance()
        cls.user = User()

        # Cleanup any mess left behind.
        cls.instance.cleanup()
        cls.project.cleanup()
        cls.user.cleanup()

        # Create 1 instance to be used in our tests which will need a project to reside in.
        project_id = cls.project.build_project("0")
        project = cls.project.get_project_data(project_id)
        if project['def_security_key_name'] == None:
            project['def_security_key_name'] = "UT_SecKeys_0"
        cls.instance.build_instance("0", project)

        # Add a power user and user to the newly created project.
        cls.user.create_and_add_puser(cls.project.get_project_by_index(0), "0")
        cls.user.create_and_add_user(cls.project.get_project_by_index(0), "0")

        return

    # Cleanup everything before we exit. This routine is only called
    # once when the class is being destroyed.
    @classmethod
    def tearDownClass(cls):
        # Cleanup our mess.
        cls.project.cleanup()
        cls.project = None
        cls.user.cleanup()
        cls.user = None
        return

    # Run anything that needs to happen before each test case is called.
    def setUp(self):
        return

    # Cleanup anything after each test case has completed.
    def tearDown(self):
        return

    # TEST CASES:

    # Test getting all instances.
    def testA_GetInstances(self):
        path = "/instances"

        # Test that we raise an exception for no authorization.
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('GET', path)
        e = cm.exception
        self.assertEqual(e.error_code, 401, "should have raised an exception, got error code %s" % e.error_code)

        # Test that we raise an exception for invalid password.
        headers = {'username': ut_config.admin, 'password': "invalid"}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('GET', path)
        e = cm.exception
        self.assertEqual(e.error_code, 401, "should have raised an exception, got error code %s" % e.error_code)

        # Test as the cloud admin.
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        data = self.rest.invoke('GET', path, headers=headers)
        instances = data['instances']

        self.assertEqual(self.instance.get_num_instances(), 1, "there should have been 1 instance found; got %s" % self.instance.get_num_instances(all_instances=True))

        valid_instances = self.instance.get_instances(all_instances=True)

        for instance in valid_instances:
            found = False
            for inst in instances:
                if inst[u'id'].encode('ascii', 'ignore') == instance['server_id']:
                    found = True
                    break
            if not found:
                self.fail("instance %s not found" % inst['name'])

        # Test as a project admin, power user and user.

        return

    # Test getting an instance.
    def testB_GetAnInstance(self):
        path = "/{project_id}/instances"

        index = 0
        proj = {}
        proj['project_id'] = self.project.get_project_by_index(index)
        proj_data = self.project.get_project_data(proj['project_id'])
                
        # Test that we raise an exception for no authorization.
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('GET', path, **proj)
        e = cm.exception
        self.assertEqual(e.error_code, 401, "should have raised an exception, got error code %s" % e.error_code)

        # Test that we raise an exception for invalid password.
        headers = {'username': ut_config.admin, 'password': "invalid"}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('GET', path, **proj)
        e = cm.exception
        self.assertEqual(e.error_code, 401, "should have raised an exception, got error code %s" % e.error_code)

        # Test that we raise an exception for a non-existant project.
        path = "/{project_id}/instances"
        proj = {}
        proj['project_id'] = "0000-0000"
                
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('GET', path, headers=headers, **proj)
        e = cm.exception
        self.assertEqual(e.error_code, 404, "should have raised an exception, got error code %s" % e.error_code)

        # Test that we get the correct data for our test instance.
        index = 0
        path = "/{project_id}/instances/{instance_id}"
        inst = {}
        inst['project_id'] = self.project.get_project_by_index(index)
        inst['instance_id'] = self.instance.get_instance_by_index(index)

        print "inst: %s" % inst

        inst_data = self.instance.get_instance_data(inst['instance_id'], inst['project_id'])
                
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        data = self.rest.invoke('GET', path, headers=headers, **inst)
        instance = data['project_id']
        self.validate_instance(instance, inst_data)

        return
        
if __name__ == "__main__":
    unittest.main(verbosity=2)

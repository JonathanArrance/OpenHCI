import unittest
import ut_config
from rest_client import RestClient
from transcirrus.common import util
import transcirrus.common.version as ver
from project import Project
import project as Proj
from user import User
import user as Usr

class ProjectTestCases(unittest.TestCase):
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
        cls.user = User()

        # Cleanup any mess left behind.
        cls.project.cleanup()
        cls.user.cleanup()

        # Create 3 projects to be used in our tests.
        cls.project.build_project("0")
        cls.project.build_project("1")
        cls.project.build_project("2")

        # Add a power user and user to each of the newly created projects.
        cls.user.create_and_add_puser(cls.project.get_project_by_index(0), "0")
        cls.user.create_and_add_puser(cls.project.get_project_by_index(1), "1")
        cls.user.create_and_add_puser(cls.project.get_project_by_index(2), "2")

        cls.user.create_and_add_user(cls.project.get_project_by_index(0), "0")
        cls.user.create_and_add_user(cls.project.get_project_by_index(1), "1")
        cls.user.create_and_add_user(cls.project.get_project_by_index(2), "2")

        # Create a 4th project by the project admin of project_0.
        proj_admin_auth = cls.project.get_auth(Proj.USERNAME_PREFIX + "0", Proj.PASSWORD_PREFIX + "0")
        cls.project.build_project("3", alt_auth=proj_admin_auth)

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

    # Test getting all projects.
    def testA_GetProjects(self):
        path = "/projects"

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
        projects = data['projects']

        valid_projs = self.project.get_projects()

        for proj in valid_projs:
            found = False
            for project in projects:
                if project[u'id'].encode('ascii','ignore') == proj:
                    found = True
                    break
            if not found:
                self.fail("project %s not found" % proj)

        # Test as the project admin 0 which has 2 projects (0 & 3).
        index = 0
        headers = {'username': Proj.USERNAME_PREFIX + str(index), 'password': Proj.PASSWORD_PREFIX + str(index)}
        data = self.rest.invoke('GET', path, headers=headers)
        projects = data['projects']

        valid_projs = []
        valid_projs.append(self.project.get_project_by_index(index))
        valid_projs.append(self.project.get_project_by_index(3))

        if len(projects) != 2:
            self.fail("incorrect number of projects found (%s)" % len(projects))

        for proj in valid_projs:
            found = False
            for project in projects:
                if project[u'id'].encode('ascii','ignore') == proj:
                    found = True
                    break
            if not found:
                self.fail("project %s not found" % proj)

        # Test as the project admin 2 which has only 1 project (2).
        index = 2
        headers = {'username': Proj.USERNAME_PREFIX + str(index), 'password': Proj.PASSWORD_PREFIX + str(index)}
        data = self.rest.invoke('GET', path, headers=headers)
        projects = data['projects']

        valid_proj = self.project.get_project_by_index(index)

        if len(projects) != 1:
            self.fail("incorrect number of projects found (%s)" % len(projects))

        for project in projects:
            if project[u'id'].encode('ascii','ignore') != valid_proj:
                self.fail("project %s not found" % valid_proj)

        # Test as a power user.
        index = 0
        headers = {'username': Usr.PWR_USER_PREFIX + str(index), 'password': Usr.PWR_USER_PWD_PREFIX + str(index)}
        data = self.rest.invoke('GET', path, headers=headers)
        projects = data['projects']

        valid_proj = self.project.get_project_by_index(index)

        if len(projects) != 1:
            self.fail("incorrect number of projects found (%s)" % len(projects))

        for project in projects:
            if project[u'id'].encode('ascii','ignore') != valid_proj:
                self.fail("project %s not found" % valid_proj)

        # Test as an user.
        index = 0
        headers = {'username': Usr.USER_PREFIX + str(index), 'password': Usr.USER_PWD_PREFIX + str(index)}
        data = self.rest.invoke('GET', path, headers=headers)
        projects = data['projects']

        valid_proj = self.project.get_project_by_index(index)

        if len(projects) != 1:
            self.fail("incorrect number of projects found (%s)" % len(projects))

        for project in projects:
            if project[u'id'].encode('ascii','ignore') != valid_proj:
                self.fail("project %s not found" % valid_proj)

        return

    # Test getting a project.
    def testB_GetAProject(self):
        path = "/projects/{project_id}"

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

        # Test as the cloud admin.
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        data = self.rest.invoke('GET', path, headers=headers, **proj)
        project = data['project']
        self.validate_project(project, proj_data)

        # Test as the project admin.
        headers = {'username': Proj.USERNAME_PREFIX + str(index), 'password': Proj.PASSWORD_PREFIX + str(index)}
        data = self.rest.invoke('GET', path, headers=headers, **proj)
        project = data['project']
        self.validate_project(project, proj_data)

        # Test as a power user.
        headers = {'username': Usr.PWR_USER_PREFIX + str(index), 'password': Usr.PWR_USER_PWD_PREFIX + str(index)}
        data = self.rest.invoke('GET', path, headers=headers, **proj)
        project = data['project']
        self.validate_project(project, proj_data)

        # Test as an user.
        headers = {'username': Usr.USER_PREFIX + str(index), 'password': Usr.USER_PWD_PREFIX + str(index)}
        data = self.rest.invoke('GET', path, headers=headers, **proj)
        project = data['project']
        self.validate_project(project, proj_data)

        # Test that we raise an exception for project admin, power user and user to non-authorized project.
        path = "/projects/{project_id}"
        proj = {}
        proj['project_id'] = self.project.get_project_by_index(1)
                
        headers = {'username': Proj.USERNAME_PREFIX + str(index), 'password': Proj.PASSWORD_PREFIX + str(index)}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('GET', path, headers=headers, **proj)
        e = cm.exception
        self.assertEqual(e.error_code, 401, "should have raised an exception, got error code %s" % e.error_code)

        headers = {'username': Usr.PWR_USER_PREFIX + str(index), 'password': Usr.PWR_USER_PWD_PREFIX + str(index)}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('GET', path, headers=headers, **proj)
        e = cm.exception
        self.assertEqual(e.error_code, 401, "should have raised an exception, got error code %s" % e.error_code)

        headers = {'username': Usr.USER_PREFIX + str(index), 'password': Usr.USER_PWD_PREFIX + str(index)}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('GET', path, headers=headers, **proj)
        e = cm.exception
        self.assertEqual(e.error_code, 401, "should have raised an exception, got error code %s" % e.error_code)

        # Test that we raise an exception for a non-existant project.
        path = "/projects/{project_id}"
        proj = {}
        proj['project_id'] = "0000-0000"
                
        headers = {'username': Proj.USERNAME_PREFIX + str(index), 'password': Proj.PASSWORD_PREFIX + str(index)}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('GET', path, headers=headers, **proj)
        e = cm.exception
        self.assertEqual(e.error_code, 404, "should have raised an exception, got error code %s" % e.error_code)

        return

    # Test creating a project.
    def testC_CreateProject(self):
        path = "/projects"
                
        # Test that we raise an exception for no authorization.
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('POST', path)
        e = cm.exception
        self.assertEqual(e.error_code, 401, "should have raised an exception, got error code %s" % e.error_code)

        # Test that we raise an exception for invalid password.
        headers = {'username': ut_config.admin, 'password': "invalid"}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('POST', path, headers=headers)
        e = cm.exception
        self.assertEqual(e.error_code, 401, "should have raised an exception, got error code %s" % e.error_code)

        # Test as the cloud admin.
        index = 4
        body = self.project.create_project_body(index)
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        data = self.rest.invoke('POST', path, headers=headers, data=body)
        proj = data['project']
        project = self.project.get_project_data(proj['id'])
        proj_data = self.project.create_project_rest_dict(index)
        self.validate_project(proj_data, project)
        self.project.delete_project_by_id(proj['id'])

        # Test as a project admin.
        index = 5
        body = self.project.create_project_body(index)
        headers = {'username': Proj.USERNAME_PREFIX + "0", 'password': Proj.PASSWORD_PREFIX + "0"}
        data = self.rest.invoke('POST', path, headers=headers, data=body)
        proj = data['project']
        project = self.project.get_project_data(proj['id'])
        proj_data = self.project.create_project_rest_dict(index)
        self.validate_project(proj_data, project)
        self.project.delete_project_by_id(proj['id'])

        # Test that we raise an exception for a power-user attempting to create a project
        index = 6
        body = self.project.create_project_body(index)
        headers = {'username': Usr.PWR_USER_PREFIX + "0", 'password': Usr.PWR_USER_PWD_PREFIX + "0"}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('POST', path, headers=headers, data=body)
        e = cm.exception
        self.assertEqual(e.error_code, 401, "should have raised an exception, got error code %s" % e.error_code)

        # Test that we raise an exception for a user attempting to create a project
        index = 6
        body = self.project.create_project_body(index)
        headers = {'username': Usr.USER_PREFIX + "0", 'password': Usr.USER_PWD_PREFIX + "0"}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('POST', path, headers=headers, data=body)
        e = cm.exception
        self.assertEqual(e.error_code, 401, "should have raised an exception, got error code %s" % e.error_code)

        # Test that we raise an exceptions for bad data
        index = 6

        ##### ENABLE once this is fixed!!

        # Bad project name
        ##body = self.project.create_project_body(index, name="?")
        ##headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        ##with self.assertRaises(Exception) as cm:
        ##    data = self.rest.invoke('POST', path, headers=headers, data=body)
        ##e = cm.exception
        ##self.assertEqual(e.error_code, 401, "should have raised an exception, got error code %s" % e.error_code)

        # Missing project name
        body = self.project.create_project_body(index, name="drop")
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('POST', path, headers=headers, data=body)
        e = cm.exception
        self.assertEqual(e.error_code, 400, "should have raised an exception (missing project name), got error code %s" % e.error_code)

        # Bad username

        # Missing username
        body = self.project.create_project_body(index, username="drop")
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('POST', path, headers=headers, data=body)
        e = cm.exception
        self.assertEqual(e.error_code, 400, "should have raised an exception (missing username), got error code %s" % e.error_code)

        # Bad password

        # Missing password
        body = self.project.create_project_body(index, password="drop")
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('POST', path, headers=headers, data=body)
        e = cm.exception
        self.assertEqual(e.error_code, 400, "should have raised an exception (missing password), got error code %s" % e.error_code)

        # Bad email address

        # Missing email address
        body = self.project.create_project_body(index, email="drop")
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('POST', path, headers=headers, data=body)
        e = cm.exception
        self.assertEqual(e.error_code, 400, "should have raised an exception (missing email), got error code %s" % e.error_code)

        ##### ENABLE once this is fixed!!

        # Duplicate email address
        ##body = self.project.create_project_body(index, email="UT_Admin_0@tc.com")
        ##headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        ##with self.assertRaises(Exception) as cm:
        ##    data = self.rest.invoke('POST', path, headers=headers, data=body)
        ##e = cm.exception
        ##self.assertEqual(e.error_code, 400, "should have raised an exception (dup email), got error code %s" % e.error_code)

        # Bad network name

        # Missing network name
        body = self.project.create_project_body(index, network_name="drop")
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('POST', path, headers=headers, data=body)
        e = cm.exception
        self.assertEqual(e.error_code, 400, "should have raised an exception (missing network name), got error code %s" % e.error_code)

        # Bad router name

        # Missing router name
        body = self.project.create_project_body(index, router_name="drop")
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('POST', path, headers=headers, data=body)
        e = cm.exception
        self.assertEqual(e.error_code, 400, "should have raised an exception (missing router name), got error code %s" % e.error_code)

        # Bad dns address

        # Missing dns address
        body = self.project.create_project_body(index, dns_address="drop")
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('POST', path, headers=headers, data=body)
        e = cm.exception
        self.assertEqual(e.error_code, 400, "should have raised an exception (missing dns), got error code %s" % e.error_code)

        # Bad security group name

        # Missing security group name
        body = self.project.create_project_body(index, security_group_name="drop")
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('POST', path, headers=headers, data=body)
        e = cm.exception
        self.assertEqual(e.error_code, 400, "should have raised an exception (missing secgroup name), got error code %s" % e.error_code)

        # Bad security_key name

        # Missing security key name
        body = self.project.create_project_body(index, security_key_name="drop")
        headers = {'username': ut_config.admin, 'password': ut_config.admin_password}
        with self.assertRaises(Exception) as cm:
            data = self.rest.invoke('POST', path, headers=headers, data=body)
        e = cm.exception
        self.assertEqual(e.error_code, 400, "should have raised an exception (missing seckey name), got error code %s" % e.error_code)

        return

    # Helper routine to validate a project dictionary.
    def validate_project(self, rest_proj, valid_proj):
        self.assertEquals(str(valid_proj['project_id']), str(rest_proj['id']), "project_id do not match %s | %s" % (valid_proj['project_id'], rest_proj['id']))
        self.assertEquals(str(valid_proj['project_name']), str(rest_proj['name']), "project_name do not match %s | %s" % (valid_proj['project_name'], rest_proj['name']))
        self.assertEquals(str(valid_proj['def_security_key_id']), str(rest_proj['security_key_id']), "security_key_id do not match %s | %s" % (valid_proj['def_security_key_id'], rest_proj['security_key_id']))
        self.assertEquals(str(valid_proj['def_security_group_id']), str(rest_proj['security_group_id']), "security_group_id do not match %s | %s" % (valid_proj['def_security_group_id'], rest_proj['security_group_id']))
        self.assertEquals(str(valid_proj['host_system_name']), str(rest_proj['host_system_name']), "host_system_name do not match %s | %s" % (valid_proj['host_system_name'], rest_proj['host_system_name']))
        self.assertEquals(str(valid_proj['host_system_ip']), str(rest_proj['host_system_ip']), "host_system_ip do not match %s | %s" % (valid_proj['host_system_ip'], rest_proj['host_system_ip']))
        self.assertEquals(str(valid_proj['def_network_name']), str(rest_proj['network_name']), "network_name do not match %s | %s" % (valid_proj['def_network_name'], rest_proj['network_name']))
        self.assertEquals(str(valid_proj['def_network_id']), str(rest_proj['network_id']), "network_id do not match %s | %s" % (valid_proj['def_network_id'], rest_proj['network_id']))
        self.assertEquals(str(valid_proj['is_default']), str(rest_proj['is_default']), "is_default do not match %s | %s" % (valid_proj['is_default'], rest_proj['is_default']))
        self.assertTrue(str(valid_proj['def_security_key_name']).startswith(str(rest_proj['security_key_name'])),  "security_key_name did not start with %s | %s" % (valid_proj['def_security_key_name'], rest_proj['security_key_name']))
        self.assertTrue(str(valid_proj['def_security_group_name']).startswith(str(rest_proj['security_group_name'])), "security_group_name did not start with %s | %s" % (valid_proj['def_security_group_name'], rest_proj['security_group_name']))
        return

if __name__ == "__main__":
    unittest.main(verbosity=2)

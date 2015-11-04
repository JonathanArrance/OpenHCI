import transcirrus.operations.build_complete_project as bldproj
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.common import extras
import transcirrus.operations.destroy_project as destroy
from transcirrus.common.auth import authorization

PROJECT_PREFIX  = "UT_Project_"
USERNAME_PREFIX = "UT_Admin_"
PASSWORD_PREFIX = "UT_pwd_"
SECGROUP_PREFIX = "UT_SecGroup_"
SECKEYS_PREFIX  = "UT_SecKeys_"
ROUTER_PREFIX   = "UT_Router_"
NETWORK_PREFIX  = "UT_Network_"
DNS_ADDR        = "8.8.8.8"

class Project:
    def __init__(self):
        self.auth = extras.shadow_auth()
        self.projects = []
        return

    def get_num_projects(self, all_projects=False):
        if all_projects:
            to = tenant_ops(self.auth)
            project_list = []
            project_list = to.list_all_tenants()
            return (len(project_list))
        else:
            return (len(self.projects))

    def build_project(self, postfix, alt_auth=None):
        user = {}
        user['username']   = USERNAME_PREFIX + str(postfix)
        user['password']   = PASSWORD_PREFIX + str(postfix)
        user['user_role']  = "admin"
        user['email']      = user['username'] + "@tc.com"
        user['project_id'] = ""

        sec_grp = {}
        sec_grp['ports']      = ""
        sec_grp['group_name'] = SECGROUP_PREFIX + str(postfix)
        sec_grp['group_desc'] = "no group desc"
        sec_grp['project_id'] = ""

        project = {}
        project['project_name']   = PROJECT_PREFIX + str(postfix)
        project['user_dict']      = user
        project['net_name']       = NETWORK_PREFIX + str(postfix)
        project['subnet_dns']     = [DNS_ADDR]
        project['sec_group_dict'] = sec_grp
        project['sec_keys_name']  = SECKEYS_PREFIX + str(postfix)
        project['router_name']    = ROUTER_PREFIX + str(postfix)

        if alt_auth != None:
            auth = alt_auth
        else:
            auth = self.auth

        project = bldproj.build_project(auth, project)
        self.projects.append(project)
        return (project)


    def get_projects(self, all_projects=False):
        if all_projects:
            to = tenant_ops(self.auth)
            project_list = []
            project_list = to.list_all_tenants()
            return (project_list)
        else:
            return (self.projects)

    def get_project_by_index(self, index):
        if len(self.projects) > index:
            return (self.projects[index])
        else:
            return (None)

    def get_project_data(self, project_id):
        to = tenant_ops(self.auth)
        project_data = to.get_tenant(project_id)
        return (project_data)

    def delete_project_by_id(self, project_id):
        to = tenant_ops(self.auth)
        proj = to.get_tenant(project_id)
        project = {}
        project['project_name'] = proj['project_name']
        project['project_id'] = project_id
        project['keep_users'] = False
        des = destroy.destroy_project(self.auth, project)
        return (True)

    def delete_project_by_index(self, index):
        self.delete_project_by_id(self.projects[index])
        return (True)

    def cleanup(self, delete_all=False):
        to = tenant_ops(self.auth)
        project_list = to.list_all_tenants()
        for project in project_list:
            if project['project_name'].startswith(PROJECT_PREFIX) or delete_all:
                self.delete_project_by_id(project['project_id'])
        return (True)

    def get_auth(self, user, password):
        a = authorization(user, password)
        auth_dict = a.get_auth()
        return auth_dict

    def create_project_body(self, postfix):
        body = {'name':                PROJECT_PREFIX + str(postfix),
                'username':            USERNAME_PREFIX + str(postfix),
                'password':            PASSWORD_PREFIX + str(postfix),
                'email':               USERNAME_PREFIX + str(postfix) + "@tc.com", 
                'network_name':        NETWORK_PREFIX + str(postfix),
                'router_name':         ROUTER_PREFIX + str(postfix),
                'dns_address':         DNS_ADDR,
                'security_group_name': SECGROUP_PREFIX + str(postfix),
                'security_key_name':   SECKEYS_PREFIX + str(postfix)
               }
        return (body)


    def create_project_rest_dict(self, postfix, id):
        proj = {}
        proj['id']                  = ""
        proj['name']                = PROJECT_PREFIX + str(postfix)
        proj['security_key_name']   = SECKEYS_PREFIX + str(postfix)
        proj['security_key_id']     = ""
        proj['security_group_id']   = ""
        proj['security_group_name'] = SECGROUP_PREFIX + str(postfix)
        proj['host_system_name']    = ""
        proj['host_system_ip']      = ""
        proj['network_name']        = NETWORK_PREFIX + str(postfix)
        proj['network_id']          = ""
        proj['is_default']          = False
        return (proj)
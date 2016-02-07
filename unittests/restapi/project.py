import time
import transcirrus.operations.build_complete_project as bldproj
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.common import extras
import transcirrus.operations.destroy_project as destroy
from transcirrus.common.auth import authorization
from transcirrus.component.neutron.layer_three import layer_three_ops

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

        try:
            des = destroy.destroy_project(self.auth, project)
        except Exception as e:
            if str(e) == "Error: Failed to remove the router internal interface.":
                l3o = layer_three_ops(self.auth)
                router_list = l3o.list_routers(project_id)
                for rtr in router_list:
                    router = l3o.get_router(rtr['router_id'])
                    proj_rout_dict = {'router_id': rtr['router_id'], 'project_id': project_id}
                    l3o.delete_router_gateway_interface(proj_rout_dict)
                    subnet_id = router["router_int_sub_id"]
                    if subnet_id:
                        remove_dict = {'router_id': rtr['router_id'], 'subnet_id': subnet_id, 'project_id': project_id}
                        l3o.delete_router_internal_interface(remove_dict)
                    del_router = l3o.delete_router(proj_rout_dict)
                    time.sleep(10)
                des = destroy.destroy_project(self.auth, project)
            else:
                raise e
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

        uo = user_ops(self.auth)
        user_list = uo.list_cloud_users()
        for user in user_list:
            if user['username'].startswith(USERNAME_PREFIX) or delete_all:
                usr = {}
                usr['username'] = user['username']
                usr['user_id'] = user['keystone_user_id']
                uo.delete_user(usr)

        return (True)

    def get_auth(self, user, password):
        a = authorization(user, password)
        auth_dict = a.get_auth()
        return auth_dict

    def create_project_body(self, postfix, name=None, username=None, password=None, email=None, network_name=None, router_name=None, dns_address=None, security_group_name=None, security_key_name=None):
        body = {}

        if name == None:
            body['name'] = PROJECT_PREFIX + str(postfix)
        elif name != "drop":
            body['name'] = name

        if username == None:
            body['username'] = USERNAME_PREFIX + str(postfix)
        elif username != "drop":
            body['username'] = username

        if password == None:
            body['password'] = PASSWORD_PREFIX + str(postfix)
        elif password != "drop":
            body['password'] = password

        if email == None:
            body['email'] = USERNAME_PREFIX + str(postfix) + "@tc.com"
        elif email != "drop":
            body['email'] = email

        if network_name == None:
            body['network_name'] = NETWORK_PREFIX + str(postfix)
        elif network_name != "drop":
            body['network_name'] = network_name

        if router_name == None:
            body['router_name'] = ROUTER_PREFIX + str(postfix)
        elif router_name != "drop":
            body['router_name'] = router_name

        if dns_address == None:
            body['dns_address'] = DNS_ADDR
        elif dns_address != "drop":
            body['dns_address'] = dns_address

        if security_group_name == None:
            body['security_group_name'] = SECGROUP_PREFIX + str(postfix)
        elif security_group_name != "drop":
            body['security_group_name'] = security_group_name

        if security_key_name == None:
            body['security_key_name'] = SECKEYS_PREFIX + str(postfix)
        elif security_key_name != "drop":
            body['security_key_name'] = security_key_name

        return (body)


    def create_project_rest_dict(self, postfix):
        projects = self.get_projects(all_projects=True)
        for project in projects:
            if project['project_name'] == PROJECT_PREFIX + str(postfix):
                data = self.get_project_data(project['project_id'])
                break

        proj = {}
        proj['id']                  = data['project_id']
        proj['name']                = PROJECT_PREFIX + str(postfix)
        proj['security_key_name']   = SECKEYS_PREFIX + str(postfix)
        proj['security_key_id']     = data['def_security_key_id']
        proj['security_group_id']   = data['def_security_group_id']
        proj['security_group_name'] = SECGROUP_PREFIX + str(postfix)
        proj['host_system_name']    = data['host_system_name']
        proj['host_system_ip']      = data['host_system_ip']
        proj['network_name']        = NETWORK_PREFIX + str(postfix)
        proj['network_id']          = data['def_network_id']
        proj['is_default']          = data['is_default']
        return (proj)

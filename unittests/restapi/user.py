from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.common import extras
import project as Proj

PWR_USER_PREFIX     = "UT_PuUser_"
PWR_USER_PWD_PREFIX = "UT_PuUser_pwd_"
USER_PREFIX         = "UT_User_"
USER_PWD_PREFIX     = "UT_User_pwd_"

class User:
    def __init__(self):
        self.auth = extras.shadow_auth()
        self.users = []
        return


    def get_num_users(self, all_users=False):
        if all_users:
            uo = user_ops(self.auth)
            user_list = []
            user_list = uo.list_cloud_users()
            return (len(user_list))
        else:
            return (len(self.users))


    def create_and_add_puser(self, project_id, user_postfix):
        user = {}
        user['username'] = PWR_USER_PREFIX + str(user_postfix)
        user['password'] = PWR_USER_PWD_PREFIX + str(user_postfix)
        user['user_role'] = "pu"
        user['email'] = user['username'] + "@tc.com"
        user['project_id'] = project_id

        user_info = self.create_user(user)
        self.users.append(user_info)
        return (user_info)


    def create_and_add_user(self, project_id, user_postfix):
        user = {}
        user['username'] = USER_PREFIX + str(user_postfix)
        user['password'] = USER_PWD_PREFIX + str(user_postfix)
        user['user_role'] = "user"
        user['email'] = user['username'] + "@tc.com"
        user['project_id'] = project_id

        user_info = self.create_user(user)
        self.users.append(user_info)
        return (user_info)


    def create_user(self, user):
        uo = user_ops(self.auth)
        user_info = uo.create_user(user)
        return (user_info)


    def get_users(self, all_users=False):
        if all_users:
            uo = user_ops(self.auth)
            user_list = []
            user_list = uo.list_cloud_users()
            return (user_list)
        else:
            return (self.users)


    def get_project_by_index(self, index):
        if len(self.users) > index:
            return (self.users[index])
        else:
            return (None)


    def delete_user(self, user_id, username):
        uo = user_ops(self.auth)
        user = {}
        user['username'] = username
        user['user_id'] = user_id
        uo.delete_user(user)
        return (True)


    def delete_user_by_index(self, index):
        self.delete_user(self.users[index]['user_id'], self.users[index]['username'])
        return (True)


    def cleanup(self, delete_all=False):
        uo = user_ops(self.auth)
        user_list = uo.list_cloud_users()
        for user in user_list:
            if user['username'].startswith(USER_PREFIX) or delete_all:
                self.delete_user(user['keystone_user_id'], user['username'])
            if user['username'].startswith(PWR_USER_PREFIX):
                self.delete_user(user['keystone_user_id'], user['username'])
        return (True)

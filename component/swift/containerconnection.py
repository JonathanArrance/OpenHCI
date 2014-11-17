import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql

import sys
sys.path.append("/usr/lib/python2.6/site-packages/")
from swiftclient import client as swiftclient
sys.path.remove("/usr/lib/python2.6/site-packages/")

class Args:
    def __init__(self, user_dict, container):
        self.username = user_dict['username']
        self.password = user_dict['password']
        self.project_id = user_dict['project_id']
        self.token = user_dict['token']
        self.status_level = user_dict['status_level']
        self.user_level = user_dict['user_level']
        self.is_admin = user_dict['is_admin']
        self.user_id = user_dict['user_id']

        self.os_auth_url = "http://" + config.API_IP + ":5000/v2.0"
        self.os_username = self.username
        self.os_password = self.password
        self.container = container

        # Get the tenant name from the DB based on project id.
        try:
            db = util.db_connect()
            get_proj = {'select': "proj_name", 'from': "projects", 'where': "proj_id='%s'" % self.project_id}
            project_name = db.pg_select(get_proj)
            if len(project_name) == 0:
                logger.sys_error("Project could not be found by ID %s" % self.project_id)
                raise Exception("Project could not be found by ID %s" % self.project_id)
            self.os_tenant_name = project_name[0][0]
        except:
            logger.sys_error("Project could not be found.")
            raise Exception("Project could not be found.")
         

class ContainerConnection(object):
    # A simple Swift interface providing just the functionality we need for containers.

    def __init__ (self, args):
        self._args = args
        self.db = util.db_connect()
        self.reset()

    def reset (self):
        # Reset the connection.
        self._con = swiftclient.Connection(
            authurl=self._args.os_auth_url,
            user=self._args.os_username,
            key=self._args.os_password,
            tenant_name=self._args.os_tenant_name,
            retries=0, auth_version='2.0')

    def exists (self, container):
        # True if the container exists.
        try:
            self._con.head_container (container)
            return True
        except swiftclient.ClientException as e:
            if e.http_status == 404:
                return False
            raise e

    def create (self, container):
        # Create the container if it doesn't already exist.
        try:
            if not self.exists (container):
                self._con.put_container (container)
                self._db_create()
        except Exception as e:
            raise e

    def list (self):
        # Return a list of all the containers for this account.
        try:
            head, containers = self._con.get_account (full_listing=True)
            return containers
        except Exception as e:
            raise e

    def delete (self, container):
        # Delete the given container.
        try:
            if self.exists (container):
                self._con.delete_container (container)
                self._db_delete()
        except Exception as e:
            raise e

    def num_objects (self, container):
        # Return the number of objects in the container as an integer.
        try:
            head, objects = self._con.get_container (container, full_listing=True)
            return (len(objects))
        except Exception as e:
            raise e

    def _db_create (self):
        try:
            put_container = None
            self.db.pg_transaction_begin()
            insert_container = {'proj_id': self._args.project_id, 'container_name': self._args.container, 'container_user_id': self._args.user_id}
            container = self.db.pg_insert ('trans_swift_containers', insert_container)
        except Exception as e:
            self.db.pg_transaction_rollback()
            logger.sys_error("Container created but not inserted into database: %s" % e)
            raise Exception("Container created but not inserted into database: %s" % e)
        self.db.pg_transaction_commit()
        return

    def _db_delete (self):
        try:
            put_container = None
            self.db.pg_transaction_begin()
            delete_container = {'table': "trans_swift_containers", 'where': "container_name='%s'" % self._args.container, 'and': "proj_id='%s'" % self._args.user_id}
            self.db.pg_delete (delete_container)
        except Exception as e:
            self.db.pg_transaction_rollback()
            logger.sys_error("Container deleted but not deleted from database: %s" % e)
            raise Exception("Container deleted but not deleted from database: %s" % e)
        self.db.pg_transaction_commit()
        return

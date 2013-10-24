import transcirrus.common.util as util
import transcirrus.common.logger as logger

from transcirrus.database.postgres import pgsql
from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.operations.change_adminuser_password import change_admin_password

#call tasks/change_admin_user_password

result = change_admin_password.delay(auth_dict,new_pass)
#check the status of the task_id
if(result.status != 'SUCCESS'):
    raise "Could not chnage the admin password, initial setup has failed."

Uplink IP
Management IP
VM range start
vm range end
cloud name
Admin password

#add all of the new value from the interface into the db


#set up service catalog - keystone will already be available
#undo and redo the keystone endpoint.

#set up all of the other endpoint based on the new mgmt IP address

#re-enable keystone

#enable nova

#enable cinder

#enable glance

#enable quantum

#after quantum enabled create the default_public ip range


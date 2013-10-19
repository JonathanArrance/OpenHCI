import transcirrus.common.util as util
import transcirrus.common.logger as logger

from transcirrus.database.postgres import pgsql
from transcirrus.component.neutron.network import neutron_net_ops
import change_adminuser_password



#call tasks/change_admin_user_password

Uplink IP
Management IP
VM range start
vm range end
cloud name
Admin password



#set up service endpoints
#undo and redo the keystone endpoint.
#set up all of the other endpoint based on the new mgmt IP address

#re-enable keystone

#enable nova

#enable cinder

#enable glance

#enable quantum
#after quantum enabled create the default_public ip range

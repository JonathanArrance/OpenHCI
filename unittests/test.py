import os
import time
import subprocess

import transcirrus.common.config as config
import transcirrus.common.util as util
import transcirrus.common.logger as logger
import transcirrus.common.node_util as node_util
import transcirrus.common.service_control as service
from transcirrus.common.auth import authorization
from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.operations.change_adminuser_password import change_admin_password
from transcirrus.component.keystone.keystone_endpoints import endpoint_ops
from transcirrus.database import node_db

c= authorization("admin","password")

print "Get admin authorization dictionary"
auth_dict = c.get_auth()

net = neutron_net_ops(auth_dict)


#connect to the DB
try:
    db = util.db_connect()
except:
    pass

#get trans_default
try:
    get_project = {'select':"*",'from':"projects",'where':"proj_name='trans_default'"}
    proj_info = db.pg_select(get_project)
except:
    pass

#get the default public info
t = None
try:
    t = net.list_networks()
except:
    pass
'''        
#get default subnet and net id
get_net = {'select':"subnet_id",'from':"trans_public_subnets",'where':"net_id='%s'"%(t[0]['net_id'])}
network = db.pg_select(get_net)
logger.sys_info("%s" %(network))

#remove the public subnet
logger.sys_info("Removeing the public subnet.")
pub_sub = net.remove_net_pub_subnet(network[0][0])
logger.sys_info("%s"%(pub_sub))
'''
#remove the public network
logger.sys_info("Removeing the public net.")
net_dict = {'net_id':t[0]['net_id'],'project_id':proj_info[0][0]}
pub_net = net.remove_network(net_dict)
logger.sys_info("%s"%(pub_net))

#import transcirrus.database.node_db as node
import transcirrus.common.util as util
import time

#print "get all of system variables"
#sys = util.get_system_variables('000-12345678-12345')
#print sys

update_dict = {'old_name':'jon-newdevstack','new_name':'jon-devstack'}
sys = util.update_cloud_controller_name(update_dict)
print sys

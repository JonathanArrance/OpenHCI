import transcirrus.database.node_db as node
import transcirrus.common.util as util
import time

print "get all of system variables"
sys = util.get_system_variables('000-12345678-12345')
print sys

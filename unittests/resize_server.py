#!/usr/bin/python
import transcirrus.operations.resize_server as resize
from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.component.nova.server_action import server_actions

a = authorization("admin","password")
#print "Get the authorization dictionary for user."
#get the user dict
d = a.get_auth()
#action = server_actions(d)
yp = {'server_id':'d7f10531-b1ce-4db2-b836-d07a588aecac','project_id':'ff8fbdc33d83419a8070d2e7577b3a3f','flavor_id':'3'}
resize.resize_and_confirm(d,yp)

#confirm = action.confirm_resize(yp)
#print confirm
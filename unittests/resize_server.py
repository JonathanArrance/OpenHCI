#!/usr/bin/python
import transcirrus.operations.resize_server as resize
from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_users import user_ops

a = authorization("admin","password")
#print "Get the authorization dictionary for user."
#get the user dict
d = a.get_auth()

yp = {'server_id':'91ace07e-7709-4301-a1b6-6a772a91a8c9','project_id':'db3161655e1e49a79c20c33a4f0e238d','flavor_id':'2'}
resize.resize_and_confirm(d,yp)
import os
import shutil

import transcirrus.operations.third_party_storage.third_party_config as tpc
import transcirrus.operations.third_party_storage.common as common
import transcirrus.operations.third_party_storage.eseries.config as eseries
import transcirrus.operations.third_party_storage.nfs.config as nfs


#
# testing some of the common functions

# test add & get param

line = "backend="
param = "test"
val = "backend=test"
if common.get_params(line) != [""]:
    raise Exception ("get_params: test failed, should have been ''")
if common.add_param(line, param) != val:
    raise Exception ("add_param: test failed, should have been %s" % val)
if common.get_params(val) != [param]:
    raise Exception ("get_params: test failed, should have been %s" % param)

line = "backend=test"
param = "next"
val = "backend=test,next"
if common.add_param(line, param) != val:
    raise Exception ("add_param: test failed, should have been %s" % val)
if common.get_params(val) != ["test", "next"]:
    raise Exception ("get_params: test failed, should have been %s" % param)

line = "backend = test, next   \n"
param = "one"
val = "backend=test,next,one"
if common.add_param(line, param) != val:
    raise Exception ("add_param: test failed, should have been %s" % val)
if common.get_params(val) != ["test", "next", "one"]:
    raise Exception ("get_params: test failed, should have been %s" % param)

# test delete param

line = "backend = test, next, one   \n"
param = "next"
val = "backend=test,one"
if common.delete_param(line, param) != val:
    raise Exception ("delete_param: test failed, should have been %s" % val)
if common.get_params(val) != ["test", "one"]:
    raise Exception ("get_params: test failed, should have been %s" % val)

line = "backend=test,one\n"
param = "one"
val = "backend=test"
if common.delete_param(line, param) != val:
    raise Exception ("delete_param: test failed, should have been %s" % val)
if common.get_params(val) != ["test"]:
    raise Exception ("get_params: test failed, should have been %s" % val)

line = "backend=test\n"
param = "test"
val = "backend="
if common.delete_param(line, param) != val:
    raise Exception ("delete_param: test failed, should have been %s" % val)
if common.get_params(val) != [""]:
    raise Exception ("get_params: test failed, should have been %s" % val)

line = "backend=test\n"
param = "shit"
val = "backend=test"
if common.delete_param(line, param) != val:
    raise Exception ("delete_param: test failed, should have been %s" % val)
if common.get_params(val) != ["test"]:
    raise Exception ("get_params: test failed, should have been %s" % val)

#
# testing e-series

# adding/getting

ret_data = tpc.get_eseries()
if ret_data['enabled'] != "0":
    raise Exception ("get eseries: test failed, enabled")

if not common.add_backend ("e-series"):
    raise Exception ("add_backend: test failed, should have been True")

ret_data = tpc.get_eseries()
if ret_data['enabled'] != "1":
    raise Exception ("add/get eseries: test failed")

if common.add_backend ("e-series"):
    raise Exception ("add_backend: test failed, should have been False")

if not common.add_backend ("test"):
    raise Exception ("add_backend: test failed, should have been True (test)")

data = {'enabled': "1", 'server': "1.2.3.4", 'srv_port': "8080", 'transport': "http", 'login': "admin", 'pwd': "password1!", 'ctrl_pwd': "cheapass1", 'disk_pools': ["Disk_Pool_1"], 'ctrl_ips': ["11.22.33.44"]}
eseries.add_eseries_stanza (data)

ret_data = tpc.get_eseries()
if ret_data != data:
    raise Exception ("add/get eseries: test failed")

if not common.delete_stanza ("e-series"):
    raise Exception ("delete_stanza: test failed, should have been True")

data = {'enabled': "1", 'server': "1.2.3.4", 'srv_port': "8080", 'transport': "http", 'login': "admin", 'pwd': "password1!", 'ctrl_pwd': "cheapass1", 'disk_pools': ["Disk_Pool_1", "Disk_Pool_2"], 'ctrl_ips': ["11.22.33.44", "55.66.77.88"]}
eseries.add_eseries_stanza (data)

ret_data = tpc.get_eseries()
if ret_data != data:
    raise Exception ("add/get eseries: test failed")

shutil.copy2("cinder.conf", "cinder.conf.add")

# deleting

if not common.delete_backend ("e-series"):
    raise Exception ("delete_backend: test failed, should have been True")

ret_data = tpc.get_eseries()
if ret_data['enabled'] != "0":
    raise Exception ("get eseries: test failed, != 0")

if common.delete_backend ("e-series"):
    raise Exception ("delete_backend: test failed, should have been False")

if not common.delete_backend ("test"):
    raise Exception ("delete_backend: test failed, should have been True (test)")

if not common.delete_stanza ("spindle"):
    raise Exception ("delete_stanza: test failed, should have been True")

if not common.delete_stanza ("e-series"):
    raise Exception ("delete_stanza: test failed, should have been True (e-series)")

shutil.copy2("cinder.conf", "cinder.conf.del")
shutil.copy2("cinder.conf.add", "cinder.conf")

# updating

data = {'enabled': "1", 'server': "001.002.003.004", 'srv_port': "8443", 'transport': "https",  'login': "administrator", 'pwd': "passw0rd", 'ctrl_pwd': "myctrlpwd", 'disk_pools': ["Disk_Pool_3"], 'ctrl_ips': ["11.22.33.44", "55.66.77.88", "99.100.101.102"]}
if not tpc.update_eseries (data):
    raise Exception ("update_eseries_stanza: test failed, should have been True")

ret_data = tpc.get_eseries()
if ret_data != data:
    raise Exception ("update/get eseries: test failed")

#
# testing nfs

ret_data = tpc.get_nfs()
if ret_data['enabled'] != "0":
    raise Exception ("get nfs: test failed")

if not common.add_backend ("nfs"):
    raise Exception ("add_backend: test failed, should have been True")

if common.add_backend ("nfs"):
    raise Exception ("add_backend: test failed, should have been False")

mountpoints = ["1.2.3.4:/mount/point"]
nfs.add_nfs_stanza()
nfs.add_nfs_conf (mountpoints)

data = {'enabled': "1", 'mountpoint': mountpoints}
ret_data = tpc.get_nfs()
if ret_data != data:
    raise Exception ("add/get nfs: test failed")

mountpoints = ["1.2.3.4:/mount/point", "nfs.test.com:/nfs/share/1"]
tpc.update_nfs (mountpoints)

data = {'enabled': "1", 'mountpoint': mountpoints}
ret_data = tpc.get_nfs()
if ret_data != data:
    raise Exception ("add/get nfs: test failed")

shutil.copy2("cinder.conf", "cinder.conf.nfs")

if not common.delete_backend ("nfs"):
    raise Exception ("delete_backend: test failed, should have been True")

ret_data = tpc.get_nfs()
if ret_data['enabled'] != "0":
    raise Exception ("get nfs: test failed")

if common.delete_backend ("nfs"):
    raise Exception ("delete_backend: test failed, should have been False")

if not common.delete_stanza ("nfs"):
    raise Exception ("delete_stanza: test failed, should have been True (e-series)")

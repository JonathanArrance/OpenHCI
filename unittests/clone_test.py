from transcirrus.common.auth import authorization
from transcirrus.operations.clone_volume import clone_volume
c= authorization("admin","password")

print "Get admin authorization dictionary"
b = c.get_auth()

clone_info = {'volume_id':'2bf22af0-9b1d-4005-8db7-b9fed877a228','project_id':'bf54175ff7594e23b8f320c74fb05d68','snapshot_id':'a32d8390-1df0-445a-b560-f38697dd3d8f','clone_type':'spindle','clone_name':'cloneit'}
yo = clone_volume(clone_info,b)
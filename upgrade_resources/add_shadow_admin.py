from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.common import extras

auth = extras.shadow_auth()
uo = user_ops(auth)
to = tenant_ops(auth)

projects = to.list_all_tenants()
for project in projects:
    try:
        print "   ***   adding shadow_admin to %s   ***" %(str(project['project_id']))
        input_dict = {'username': 'shadow_admin', 'user_role': 'admin', 'project_id': project['project_id']}
        print uo.add_user_to_project(input_dict)
    except:
        continue

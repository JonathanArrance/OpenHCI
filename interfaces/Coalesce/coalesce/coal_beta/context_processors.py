from django.conf import settings
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.database.node_db import list_nodes

def global_vars(request):
    try:
        auth = request.session['auth']
        to = tenant_ops(auth)
        project_list = to.list_all_tenants()
        token = auth['token']
    except:
        project_list = []
        token = ""
    node_list = list_nodes()


    return {'node_list': node_list, 'project_list': project_list, 'token': token}
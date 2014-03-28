from django.conf import settings
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.database.node_db import list_nodes

def global_vars(request):
    try:
        auth = request.session['auth']
        token = auth['token']
        username = auth['username']
        user_level = auth['user_level']
        project_id = auth['project_id']
    except:
        token = ""
        username=""
        project_id=""
        user_level="3"



    return {'username': username, 
            'user_level': user_level,
            'project_id': project_id,
            'token': token}
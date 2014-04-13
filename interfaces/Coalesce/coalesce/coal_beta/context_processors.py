from django.conf import settings
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.database.node_db import list_nodes
from transcirrus.common import node_util

def global_vars(request):
    try:
        auth = request.session['auth']
        token = auth['token']
        username = auth['username']
        user_level = auth['user_level']
        project_id = auth['project_id']
        boot = node_util.check_first_time_boot()
        first_time = boot['first_time_boot']
    except:
        token = ""
        username=""
        project_id=""
        user_level="3"
        first_time='FALSE'



    return {'username': username,
            'user_level': user_level,
            'project_id': project_id,
            'token': token,
            'first_time': first_time}
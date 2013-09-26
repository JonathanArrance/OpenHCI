from django.conf import settings
from coalesce.coal_beta.models import Node, Project
from transcirrus.component.keystone_tenant import *

def global_vars(request):

    project_list = Project.objects.all()
    #project_list = tenant_ops.list_all_tenants
    node_list = Node.objects.all()
    return {'node_list': node_list, 'project_list': project_list}
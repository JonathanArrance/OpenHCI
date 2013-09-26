# Django imports
from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import Http404
from django.conf import settings
from django_tables2   import RequestConfig
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError
from django.db import connection

# Python imports
from datetime import datetime
from collections import defaultdict
import csv
# Custom imports
from coalesce.coal_beta.models import *

def welcome(request):
    request.session["return_url"] = '/'
    return render_to_response('coal/welcome.html', RequestContext(request, ))


def privacy_policy(request):
    return render_to_response('coal/privacy-policy.html', RequestContext(request,))

def disclaimer(request):
    return render_to_response('coal/website-disclaimer.html', RequestContext(request,))


def terms_of_use(request):
    return render_to_response('coal/terms-of-use.html', RequestContext(request,))


@login_required()
def node_view(request, node_name):
    node = Node.objects.get(name=node_name)
    return render_to_response('coal/node_view.html', RequestContext(request, {'node': node, }))

@login_required()
def manage_nodes(request):
    nodes = Node.objects.all()
    nodes_table = NodesTable(nodes)
    RequestConfig(request).configure(nodes_table)
    return render_to_response('coal/manage_nodes.html', RequestContext(request, {'nodes_table':nodes_table}))

@login_required()
def project_view(request, project_id):
    project = Project.objects.get(pk=project_id)
    return render_to_response('coal/project_view.html', RequestContext(request, {'project': project, }))

@login_required()
def manage_projects(request):
    projects = Project.objects.all()
    projects_table = ProjectsTable(projects)
    RequestConfig(request).configure(projects_table)
    return render_to_response('coal/manage_projects.html', RequestContext(request, { 'projects_table':projects_table}))


# --- Media ---
def logo(request):
    image_data = open(r'%s\static\\transcirrus_weblogo.png' % settings.PROJECT_PATH, 'rb').read()

    return HttpResponse(image_data, mimetype="image/gif")

# --- Javascript ---
def jq(request):
    file = open(r'%s\javascripts\\jquery-latest.pack.js' % settings.PROJECT_PATH, 'rb').read()
    return HttpResponse(file, mimetype="text/javascript")

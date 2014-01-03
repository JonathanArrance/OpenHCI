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
from django.views.decorators.cache import never_cache


from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.component.nova.server import server_ops
from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.operations.initial_setup import run_setup
from transcirrus.operations.change_adminuser_password import change_admin_password
import transcirrus.common.util as util

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template.response import TemplateResponse

# Python imports
from datetime import datetime
from collections import defaultdict
import csv
# Custom imports
from coalesce.coal_beta.models import *
from coalesce.coal_beta.forms import *


def welcome(request):

    return render_to_response('coal/welcome.html', RequestContext(request, ))


def privacy_policy(request):
    return render_to_response('coal/privacy-policy.html', RequestContext(request,))

def disclaimer(request):
    return render_to_response('coal/website-disclaimer.html', RequestContext(request,))


def terms_of_use(request):
    return render_to_response('coal/terms-of-use.html', RequestContext(request,))



def node_view(request, node_name):
    node = Node.objects.get(name=node_name)
    return render_to_response('coal/node_view.html', RequestContext(request, {'node': node, }))

def manage_nodes(request):
    nodes = Node.objects.all()
    nodes_table = NodesTable(nodes)
    RequestConfig(request).configure(nodes_table)
    return render_to_response('coal/manage_nodes.html', RequestContext(request, {'nodes_table':nodes_table}))

def project_view(request, project_name):
    auth = request.session['auth']
    to = tenant_ops(auth)
    so = server_ops(auth)
    no = neutron_net_ops(auth)
    
    project = to.get_tenant(project_name)
    users = to.list_tenant_users(project_name)
    network_list = no.list_networks()
    networks={}
    for net in network_list:
      networks[net['net_name']]= no.get_network(net['net_name'])
    sec_groups = so.list_sec_group()
    sec_keys = so.list_sec_keys()
    print '~~~~~~~~~~~~~~~~~~~~~~~'
    print sec_groups
    print '~~~~~~~~~~~~~~~~~~~~~~~'
    print sec_keys
    print '~~~~~~~~~~~~~~~~~~~~~~~'
    return render_to_response('coal/project_view.html', RequestContext(request, {'project': project, 'users': users, 'sec_groups': sec_groups,  'sec_keys': sec_keys, 'networks': networks}))


def manage_projects(request):
    projects = Project.objects.all()
    projects_table = ProjectsTable(projects)
    RequestConfig(request).configure(projects_table)
    return render_to_response('coal/manage_projects.html', RequestContext(request, { 'projects_table':projects_table}))


def setup(request):
    if request.method == 'POST':
        form = SetupForm(request.POST)
        if form.is_valid():
            management_ip = form.cleaned_data['management_ip']
            uplink_ip = form.cleaned_data['uplink_ip']
            vm_ip_min = form.cleaned_data['vm_ip_min']
            vm_ip_max = form.cleaned_data['vm_ip_max']
            uplink_dns = form.cleaned_data['uplink_dns']
            uplink_gateway = form.cleaned_data['uplink_gateway']
            uplink_domain_name = form.cleaned_data['uplink_domain_name']
            uplink_subnet = form.cleaned_data['uplink_subnet']
            mgmt_domain_name = form.cleaned_data['mgmt_domain_name']
            mgmt_subnet = form.cleaned_data['mgmt_subnet']
            mgmt_dns = form.cleaned_data['mgmt_dns']
            cloud_name  = form.cleaned_data['cloud_name']
            single_node = form.cleaned_data['single_node']
            admin_password = form.cleaned_data['admin_password']
            admin_password_confirm = form.cleaned_data['admin_password_confirm']

	    auth = request.session['auth']

	    system = util.get_cloud_controller_name()
	    system_var_array = [
                        {"system_name": system, "parameter": "api_ip",             "param_value": uplink_ip},
                        {"system_name": system, "parameter": "mgmt_ip",            "param_value": management_ip},
                        {"system_name": system, "parameter": "admin_api_ip",       "param_value": uplink_ip},
                        {"system_name": system, "parameter": "int_api_id",         "param_value": uplink_ip},
                        {"system_name": system, "parameter": "uplink_ip",          "param_value": uplink_ip},
                        {"system_name": system, "parameter": "vm_ip_min",          "param_value": vm_ip_min},
                        {"system_name": system, "parameter": "vm_ip_max",          "param_value": vm_ip_max},
                        {"system_name": system, "parameter": "single_node",        "param_value": single_node},
                        {"system_name": system, "parameter": "uplink_dns",         "param_value": uplink_dns},
			{"system_name": system, "parameter": "uplink_gateway",     "param_value": uplink_gateway},
			{"system_name": system, "parameter": "uplink_domain_name", "param_value": uplink_domain_name},
			{"system_name": system, "parameter": "uplink_subnet",      "param_value": uplink_subnet},
			{"system_name": system, "parameter": "mgmt_domain_name",   "param_value": mgmt_domain_name},
			{"system_name": system, "parameter": "mgmt_subnet",        "param_value": mgmt_subnet},
			{"system_name": system, "parameter": "mgmt_dns",           "param_value": mgmt_dns},
                        ]

	    run_setup(system_var_array, auth)
	    change_admin_password (auth, admin_password)

            if request.POST.get('cancel'):
                return HttpResponseRedirect('/')
            else:
                return render_to_response('coal/setup_results.html', RequestContext(request, {'cloud_name':cloud_name, 'management_ip': management_ip}))

    else:
        form = SetupForm()
    return render_to_response('coal/setup.html', RequestContext(request, { 'form':form, }))

# --- Media ---
def logo(request):
    image_data = open(r'%s\static\\transcirrus_weblogo.png' % settings.PROJECT_PATH, 'rb').read()

    return HttpResponse(image_data, mimetype="image/gif")

# --- Javascript ---
def jq(request):
    file = open(r'%s\javascripts\\jquery-latest.pack.js' % settings.PROJECT_PATH, 'rb').read()
    return HttpResponse(file, mimetype="text/javascript")

# ---- Authentication ---

@never_cache
def login_page(request, template_name):

    if request.method == "POST":
        form = authentication_form(request.POST)
        if form.is_valid():

            # Okay, security check complete. Log the user in.
            user = form.cleaned_data['username']
            pw = form.cleaned_data['password']
            a = authorization(user, pw)
            auth = a.get_auth()
            request.session['auth'] = auth
            print auth


            return render_to_response('coal/welcome.html', RequestContext(request, {  }))
    else:
        form = authentication_form()

        return render_to_response('coal/login.html', RequestContext(request, { 'form':form, }))

@never_cache
def logout(request, next_page=None,
           template_name='coal/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           current_app=None, extra_context=None):
    """
    Logs out the user and displays 'You are logged out' message.
    """
    auth_logout(request)

    if redirect_field_name in request.REQUEST:
        next_page = request.REQUEST[redirect_field_name]
        # Security check -- don't allow redirection to a different host.
        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = request.path

    if next_page:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page)

    current_site = get_current_site(request)
    context = {
        'site': current_site,
        'site_name': current_site.name,
        'title': ('Logged out')
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
        current_app=current_app)


@never_cache
def password_change(request):
    return render_to_response('coal/change-password.html', RequestContext(request, {  }))

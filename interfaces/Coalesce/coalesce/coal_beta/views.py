# Django imports
from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
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
from django.core import serializers
import time


from transcirrus.common.auth import authorization
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.component.nova.server import server_ops
from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.cinder.cinder_volume import volume_ops
from transcirrus.component.cinder.cinder_snapshot import snapshot_ops
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
from django.views.decorators.csrf import csrf_protect, csrf_exempt


# Python imports
from datetime import datetime
from collections import defaultdict
import csv
import json
from urlparse import urlsplit

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
    l3o = layer_three_ops(auth)
    vo = volume_ops(auth)
    sno = snapshot_ops(auth)

    project = to.get_tenant(project_name)
    pid = project["project_id"]
    users = to.list_tenant_users(project_name)
    userinfo = {}
    uo = user_ops(auth)

    for user in users:
        user_dict = {'username': user['username'], 'project_name': project_name}
        user_info = uo.get_user_info(user_dict)
        userinfo[user['username']] = user_info 
     
    try:
        ousers = uo.list_orphaned_users()
    except:
        raise
   
    ouserinfo = []
    if ousers:
        for ouser in ousers:
            ouserinfo.append(ouser['user_name'])     
  
    network_list = no.list_networks()
    routers= l3o.list_routers()
    volumes = vo.list_volumes(pid)
    snapshots=sno.list_snapshots()
    sec_groups = so.list_sec_group()
    sec_keys = so.list_sec_keys()

    networks={}
    for net in network_list:
        networks[net['net_name']]= no.get_network(net['net_id'])


    return render_to_response('coal/project_view.html',
                               RequestContext(request, { 'project': project,
                                                        'users': users,
                                                        'ouserinfo': ouserinfo,
                                                        'userinfo':userinfo,
                                                        'sec_groups': sec_groups,
                                                        'sec_keys': sec_keys,
                                                        'networks': networks,
                                                        'routers': routers,
                                                        'volumes': volumes,
                                                        'snapshots':snapshots,
                                                        }))

def user_view(request, project_name, user_name):
    auth = request.session['auth']
    uo = user_ops(auth)
    user_dict = {'username': user_name, 'project_name': project_name}
    user_info = uo.get_user_info(user_dict)

    return render_to_response('coal/user_view.html',
                               RequestContext(request, { 'project_name': project_name,
                                                        'user_info': user_info,
                                                        }))

def volume_view(request, project_id, vol_id):
    auth = request.session['auth']
    vo = volume_ops(auth)
    sno = snapshot_ops(auth)
    snapshots = sno.list_snapshots()
    vol_dict = {'project_id': project_id, 'vol_id': vol_id}
    volume_info = vo.get_volume_info(vol_dict)

    return render_to_response('coal/volume_view.html',
                               RequestContext(request, { 'project_id' : project_id,
                                                        'volume_info': volume_info,
							'snapshots': snapshots,
                                                        }))
	       	       

def create_user(request, username, password, userrole, email, project_id):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'password':password, 'userrole':userrole, 'email': email, 'project_id': project_id}
	#import pdb; pdb.set_trace()
        newuser= uo.create_user(user_dict)
        return HttpResponseRedirect("project_view", )
    except:
        raise


def create_security_group(request, groupname, groupdesc, ports, project_id):
    try:
	portstrings    = ports.split(',')
	portlist = []
	for port in portstrings:
	    portlist.append(int(port))
        auth = request.session['auth']
        so = server_ops(auth)
        create_sec = {'group_name': groupname, 'group_desc':groupdesc, 'ports': portlist, 'project_id': project_id}
        newgroup= so.create_sec_group(create_sec)  
        print "newgroup = %s" % newgroup
	return HttpResponseRedirect("manage_projects")
    except:
        return HttpResponse(status=500)

def create_keypair(request, key_name, project_id):
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        key_dict = {'key_name': key_name, 'project_id': project_id}
        newkey= so.create_sec_keys(key_dict)  
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        return HttpResponse(status=500)

def create_volume(request, volume_name, volume_size, description, project_id):
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        create_vol = {'volume_name': volume_name, 'volume_size': volume_size, 'description': description, 'project_id': project_id}
        vo.create_volume(create_vol)  
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        return HttpResponse(status=500)

def take_snapshot(request, snap_name, snap_desc, vol_id, project_id):
    try:
        auth = request.session['auth']
        sno = snapshot_ops(auth)
        create_snap = {'snap_name': snap_name, 'snap_desc': snap_desc, 'vol_id': vol_id, 'project_id': project_id}
        sno.create_snapshot(create_snap)  
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        return HttpResponse(status=500)
      
      
def toggle_user(request, username, toggle):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'toggle':toggle}
        uo.toggle_user(user_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        return HttpResponse(status=500)
      
def delete_user(request, username, userid):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'userid':userid}
        uo.delete_user(user_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        return HttpResponse(status=500)
      
def remove_user_from_project(request, user_id, project_id):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'user_id': user_id, 'project_id':project_id}
        uo.remove_user_from_project(user_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        return HttpResponse(status=500)
      
def add_existing_user(request, username, user_role, project_name):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'user_role':user_role, 'project_name': project_name}
        uo.add_user_to_project(user_dict)
	referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        return HttpResponse(status=500)  


def update_user_password(request, user_id, project_id, new_password):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'user_id': user_id, 'project_id':project_id}
        uo.remove_user_from_project(user_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        return HttpResponse(status=500)  

def network_view(request, net_id):
    auth = request.session['auth']
    no = neutron_net_ops(auth)
    nw = no.get_network(net_id)

    return render_to_response('coal/network_view.html',
                               RequestContext(request, {
                                                        'nw': nw,
                                                        }))

def add_private_network(request, net_name, admin_state, shared, project_id, subnet_dhcp_enable, subnet_dns):
    try:
        auth = request.session['auth']
        no = neutron_net_ops(auth)
        create_dict = {"net_name": net_name, "admin_state": admin_state, "shared": shared, "project_id": project_id}
        network = no.add_private_network(create_dict)
	
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        return HttpResponse(status=500)



def manage_projects(request):
    projects = Project.objects.all()
    projects_table = ProjectsTable(projects)
    RequestConfig(request).configure(projects_table)
    return render_to_response('coal/manage_projects.html', RequestContext(request, { 'projects_table':projects_table}))


def setup(request):
    if request.method == 'POST':
        form = SetupForm(request.POST)
        if form.is_valid():
            management_ip 		= form.cleaned_data['management_ip']
            uplink_ip 			= form.cleaned_data['uplink_ip']
            vm_ip_min 			= form.cleaned_data['vm_ip_min']
            vm_ip_max 			= form.cleaned_data['vm_ip_max']
            uplink_dns 			= form.cleaned_data['uplink_dns']
            uplink_gateway 		= form.cleaned_data['uplink_gateway']
            uplink_domain_name 		= form.cleaned_data['uplink_domain_name']
            uplink_subnet 		= form.cleaned_data['uplink_subnet']
            mgmt_domain_name 		= form.cleaned_data['mgmt_domain_name']
            mgmt_subnet 		= form.cleaned_data['mgmt_subnet']
            mgmt_dns 			= form.cleaned_data['mgmt_dns']
            cloud_name  		= form.cleaned_data['cloud_name']
            single_node 		= form.cleaned_data['single_node']
            admin_password 		= form.cleaned_data['admin_password']
            admin_password_confirm 	= form.cleaned_data['admin_password_confirm']

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


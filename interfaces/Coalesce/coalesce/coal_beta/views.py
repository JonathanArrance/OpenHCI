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
from transcirrus.component.nova.storage import server_storage_ops
from transcirrus.component.nova.server_action import server_actions
from transcirrus.component.nova.admin_actions import server_admin_actions
from transcirrus.component.neutron.network import neutron_net_ops
from transcirrus.component.neutron.layer_three import layer_three_ops
from transcirrus.component.cinder.cinder_volume import volume_ops
from transcirrus.component.cinder.cinder_snapshot import snapshot_ops
from transcirrus.component.glance.glance_ops_v2 import glance_ops
from transcirrus.component.nova.flavor import flavor_ops
from transcirrus.component.swift.container_services import container_service_ops
from transcirrus.component.swift.account_services import account_service_ops
from transcirrus.operations.initial_setup import run_setup
import transcirrus.operations.build_complete_project as bcp
from transcirrus.operations.change_adminuser_password import change_admin_password
import transcirrus.common.util as util
from transcirrus.database.node_db import list_nodes, get_node
import transcirrus.operations.destroy_project as destroy

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib import messages


# Python imports
from datetime import datetime
from collections import defaultdict
import csv
import json
import sys
from urlparse import urlsplit

# Custom imports
#from coalesce.coal_beta.models import *
from coalesce.coal_beta.forms import *

def welcome(request):
    return render_to_response('coal/welcome.html', RequestContext(request, ))

def privacy_policy(request):
    return render_to_response('coal/privacy-policy.html', RequestContext(request,))

def disclaimer(request):
    return render_to_response('coal/website-disclaimer.html', RequestContext(request,))

def terms_of_use(request):
    return render_to_response('coal/terms-of-use.html', RequestContext(request,))

def node_view(request, node_id):
    node=get_node(node_id)
    return render_to_response('coal/node_view.html', RequestContext(request, {'node': node, }))

def manage_cloud(request):
    node_list = list_nodes()
    node_info = []
    auth = request.session['auth']
    to = tenant_ops(auth)
    project_list = to.list_all_tenants()
    project_info = []
    try:
        for node in node_list:
            nid = node['node_id']
            ni = get_node(nid)
            ni['node_id']= nid
            node_info.append(ni)
    except TypeError:
        pass
    try:
        for proj in project_list:
            pid = proj['project_id']
            dict={}
            pi = to.get_tenant(pid)
            project_info.append(pi)
    except:
        messages.warning(request, "Unable to manage cloud.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render_to_response('coal/manage_cloud.html', RequestContext(request, {'project_info': project_info, 'node_info': node_info}))

def manage_nodes(request):
    node_list = list_nodes()
    node_info = []
    try:
        for node in node_list:
            nid = node['node_id']
            ni = get_node(nid)
            ni['node_id']= nid
            node_info.append(ni)
    except:
        messages.warning(request, "Unable to manage nodes.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render_to_response('coal/manage_nodes.html', RequestContext(request, {'node_info': node_info,}))

def manage_projects(request):
    auth = request.session['auth']
    to = tenant_ops(auth)
    project_list = to.list_all_tenants()
    project_info = []
    try:
        for proj in project_list:
            pid = proj['project_id']
            dict={}
            pi = to.get_tenant(pid)
            project_info.append(pi)
    except:
        messages.warning(request, "Unable to manage projects.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render_to_response('coal/manage_projects.html', RequestContext(request, {'project_info': project_info,}))

def project_view(request, project_id):
    auth = request.session['auth']
    to = tenant_ops(auth)
    so = server_ops(auth)
    no = neutron_net_ops(auth)
    l3o = layer_three_ops(auth)
    vo = volume_ops(auth)
    sno = snapshot_ops(auth)
    go = glance_ops(auth)
    ssa = server_admin_actions(auth)
    fo = flavor_ops(auth)
    cso = container_service_ops(auth)
    aso = account_service_ops(auth)

    project = to.get_tenant(project_id)
    users = to.list_tenant_users(project_id)
    userinfo = {}
    uo = user_ops(auth)

    for user in users:
        user_dict = {'username': user['username'], 'project_name': project['project_name']}
        user_info = uo.get_user_info(user_dict)
        userinfo[user['username']] = user_info

    ouserinfo = []
    try:
        ousers = uo.list_orphaned_users()
        if ousers:
            for ouser in ousers:
                ouserinfo.append(ouser['username'])
    except:
        ousers=[]

    priv_net_list = no.list_internal_networks(project_id)
    pub_net_list  = no.list_external_networks()
    routers       = l3o.list_routers(project_id)
    volumes       = vo.list_volumes(project_id)
    volume_info={}
    snapshots     = sno.list_snapshots(project_id)
    try:
        containers    = aso.get_account_containers(project_id)
    except:
        containers = []
    sec_groups    = so.list_sec_group(project_id)
    sec_keys      = so.list_sec_keys(project_id)
    instances     = so.list_servers(project_id)
    instance_info={}
    flavors       = fo.list_flavors()
    
    hosts=[]
    host_dict     = {'project_id': project_id, 'zone': 'nova'}
    hosts         = ssa.list_compute_hosts(host_dict)
    
    for volume in volumes:
        v_dict = {'volume_id': volume['volume_id'], 'project_id': project['project_id']}
        v_info = vo.get_volume_info(v_dict)
        vid = volume['volume_id']
        volume_info[vid] = v_info
    
    for instance in instances:
        i_dict = {'server_id': instance['server_id'], 'project_id': project['project_id']}
        try:
            i_info = so.get_server(i_dict)
            sname  = instance['server_name']
            instance_info[sname] = i_info
        except Exception:
            sys.exc_clear()
            i_info = {'server_os': '',
                      'server_key_name': '',
                      'server_group_name': '',
                      'server_zone': '',
                      'server_public_ips': {},
                      'server_id': '',
                      'server_name': instance['server_name'],
                      'server_status': u'BUILDING',
                      'server_node': '',
                      'server_int_net': {},
                      'server_net_id': '',
                      'server_flavor': ''}
            sname = instance['server_name']
            instance_info[sname] = i_info
            
    try:
        images    = go.list_images()
    except:
        images =[]

    private_networks={}
    for net in priv_net_list:
        try:
            private_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    public_networks={}
    for net in pub_net_list:
        try:
            public_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    try:
        default_public = public_networks.values()[0]['net_id'] # <<< THIS NEEDS TO CHANGE IF MULTIPLE PUB NETWORKS EXIST
    except:
        default_public = "NO PUBLIC NETWORK"

    floating_ips = l3o.list_floating_ips(project_id)
    for fip in floating_ips:
        if fip["floating_in_use"]:
            ip_info =l3o.get_floating_ip(fip['floating_ip_id'])
            fip['instance_name']=ip_info['instance_name']
        else:
            fip['instance_name']=''

    return render_to_response('coal/project_view.html',
                               RequestContext(request, {'project': project,
                                                        'users': users,
                                                        'ouserinfo': ouserinfo,
                                                        'userinfo':userinfo,
                                                        'sec_groups': sec_groups,
                                                        'sec_keys': sec_keys,
                                                        'private_networks': private_networks,
                                                        'public_networks': public_networks,
                                                        'default_public': default_public,
                                                        'priv_net_list':priv_net_list,
                                                        'pub_net_list':pub_net_list,
                                                        'routers': routers,
                                                        'floating_ips': floating_ips,
                                                        'hosts': hosts,
                                                        'volumes': volumes,
                                                        'volume_info': volume_info,
                                                        'snapshots': snapshots,
                                                        'containers': containers,
                                                        'images': images,
                                                        'instances': instances,
                                                        'instance_info': instance_info,
                                                        'flavors': flavors
                                                        }))
def pu_project_view(request, project_id):
    auth = request.session['auth']
    to = tenant_ops(auth)
    so = server_ops(auth)
    no = neutron_net_ops(auth)
    l3o = layer_three_ops(auth)
    vo = volume_ops(auth)
    sno = snapshot_ops(auth)
    go = glance_ops(auth)
    fo = flavor_ops(auth)
    cso = container_service_ops(auth)
    aso = account_service_ops(auth)

    project = to.get_tenant(project_id)
    users = to.list_tenant_users(project_id)
    userinfo = {}
    uo = user_ops(auth)

    for user in users:
        user_dict = {'username': user['username'], 'project_name': project['project_name']}
        user_info = uo.get_user_info(user_dict)
        userinfo[user['username']] = user_info

    ouserinfo = []
    try:
        ousers = uo.list_orphaned_users()
        if ousers:
            for ouser in ousers:
                ouserinfo.append(ouser['username'])
    except:
        ousers=[]

    priv_net_list = no.list_internal_networks(project_id)
    pub_net_list  = no.list_external_networks()
    routers       = l3o.list_routers(project_id)
    volumes       = vo.list_volumes(project_id)
    volume_info={}
    snapshots     = sno.list_snapshots(project_id)
    sec_groups    = so.list_sec_group(project_id)
    sec_keys      = so.list_sec_keys(project_id)
    instances     = so.list_servers(project_id)
    instance_info={}
    flavors       = fo.list_flavors()
    
    for volume in volumes:
        v_dict = {'volume_id': volume['volume_id'], 'project_id': project['project_id']}
        v_info = vo.get_volume_info(v_dict)
        vid = volume['volume_id']
        volume_info[vid] = v_info
    
    for instance in instances:
        i_dict = {'server_id': instance['server_id'], 'project_id': project['project_id']}
        try:
            i_info = so.get_server(i_dict)
            sname  = instance['server_name']
            instance_info[sname] = i_info
        except Exception:
            sys.exc_clear()
            i_info = {'server_os': '',
                      'server_key_name': '',
                      'server_group_name': '',
                      'server_zone': '',
                      'server_public_ips': {},
                      'server_id': '',
                      'server_name': instance['server_name'],
                      'server_status': u'BUILDING',
                      'server_node': '',
                      'server_int_net': {},
                      'server_net_id': '',
                      'server_flavor': ''}
            sname = instance['server_name']
            instance_info[sname] = i_info
            
    try:
        images    = go.list_images()
    except:
        images =[]

    private_networks={}
    for net in priv_net_list:
        try:
            private_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    public_networks={}
    for net in pub_net_list:
        try:
            public_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    try:
        default_public = public_networks.values()[0]['net_id'] # <<< THIS NEEDS TO CHANGE IF MULTIPLE PUB NETWORKS EXIST
    except:
        default_public = "NO PUBLIC NETWORK"

    floating_ips = l3o.list_floating_ips(project_id)
    for fip in floating_ips:
        if fip["floating_in_use"]:
            ip_info =l3o.get_floating_ip(fip['floating_ip_id'])
            fip['instance_name']=ip_info['instance_name']
        else:
            fip['instance_name']=''

    return render_to_response('coal/project_view.html',
                               RequestContext(request, {'project': project,
                                                        'users': users,
                                                        'ouserinfo': ouserinfo,
                                                        'userinfo':userinfo,
                                                        'sec_groups': sec_groups,
                                                        'sec_keys': sec_keys,
                                                        'private_networks': private_networks,
                                                        'public_networks': public_networks,
                                                        'default_public': default_public,
                                                        'priv_net_list':priv_net_list,
                                                        'pub_net_list':pub_net_list,
                                                        'routers': routers,
                                                        'floating_ips': floating_ips,
                                                        'volumes': volumes,
                                                        'volume_info': volume_info,
                                                        'snapshots':snapshots,
                                                        'images': images,
                                                        'instances': instances,
                                                        'instance_info': instance_info,
                                                        'flavors': flavors
                                                        }))
def basic_project_view(request, project_id):
    auth = request.session['auth']
    to = tenant_ops(auth)
    project = to.get_tenant(project_id)
    vo = volume_ops(auth)
    go = glance_ops(auth)
    so = server_ops(auth)
    l3o = layer_three_ops(auth)
    no = neutron_net_ops(auth)
    fo = flavor_ops(auth)
    volumes       = vo.list_volumes(project_id)
    volume_info={}
    sec_groups    = so.list_sec_group(project_id)
    sec_keys      = so.list_sec_keys(project_id)
    instances     = so.list_servers(project_id)
    flavors       = fo.list_flavors()
    #pub_net_list  = no.list_external_networks()

    for volume in volumes:
        v_dict = {'volume_id': volume['volume_id'], 'project_id': project['project_id']}
        v_info = vo.get_volume_info(v_dict)
        vid = volume['volume_id']
        volume_info[vid] = v_info
    
    priv_net_list = no.list_internal_networks(project_id)
    private_networks={}
    for net in priv_net_list:
        try:
            private_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass



    instance_info={}
    for instance in instances:
        i_dict = {'server_id': instance['server_id'], 'project_id': project['project_id']}
        try:
            i_info = so.get_server(i_dict)
            sname  = instance['server_name']
            instance_info[sname] = i_info
        except Exception:
            sys.exc_clear()
            i_info = {'server_os': '',
                      'server_key_name': '',
                      'server_group_name': '',
                      'server_zone': '',
                      'server_public_ips': {},
                      'server_id': '',
                      'server_name': instance['server_name'],
                      'server_status': u'BUILDING',
                      'server_node': '',
                      'server_int_net': {},
                      'server_net_id': '',
                      'server_flavor': ''}
            sname = instance['server_name']
            instance_info[sname] = i_info

    try:
        images    = go.list_images()
    except:
        images =[]

    floating_ips = l3o.list_floating_ips(project_id)
    for fip in floating_ips:
        if fip["floating_in_use"]:
            ip_info =l3o.get_floating_ip(fip['floating_ip_id'])
            fip['instance_name']=ip_info['instance_name']
        else:
            fip['instance_name']=''

    pub_net_list  = no.list_external_networks()

    public_networks={}
    for net in pub_net_list:
        try:
            public_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    try:
        default_public = public_networks.values()[0]['net_id'] # <<< THIS NEEDS TO CHANGE IF MULTIPLE PUB NETWORKS EXIST
    except:
        default_public = "NO PUBLIC NETWORK"

    """
1. create a vm
2. provision a new volume
3. upload download delete swift objects
4. add available floating ip to an instance
5. remove a floating ip from an instance
we need to build a function to request a vm resize
6. delete a vm that they own
7. confirm resize of an instance
8. revert instance back to original size
9. get the status of the instance
10. get the novnc console of an instance
3. delete volumes they own
11 attach volumes to
12 detach vols from instances they own
13 update their password
14. list the vms they own






    sno = snapshot_ops(auth)


    project = to.get_tenant(project_id)
    users = to.list_tenant_users(project_id)
    userinfo = {}
    uo = user_ops(auth)

    for user in users:
        user_dict = {'username': user['username'], 'project_name': project['project_name']}
        user_info = uo.get_user_info(user_dict)
        userinfo[user['username']] = user_info

    try:
        ousers = uo.list_orphaned_users()
    except:
        raise

    ouserinfo = []
    if ousers:
        for ouser in ousers:
            ouserinfo.append(ouser['username'])


    pub_net_list  = no.list_external_networks()
    routers       = l3o.list_routers(project_id)

    snapshots     = sno.list_snapshots(project_id)



    private_networks={}
    for net in priv_net_list:
        try:
            private_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    public_networks={}
    for net in pub_net_list:
        try:
            public_networks[net['net_name']]= no.get_network(net['net_id'])
        except:
            pass

    try:
        default_public = public_networks.values()[0]['net_id'] # <<< THIS NEEDS TO CHANGE IF MULTIPLE PUB NETWORKS EXIST
    except:
        default_public = "NO PUBLIC NETWORK"


    """

    return render_to_response('coal/basic_project_view.html',
                               RequestContext(request, {'project': project,
                                                        'sec_groups': sec_groups,
                                                        'sec_keys': sec_keys,
                                                        'volumes': volumes,
                                                        'volume_info':volume_info,
                                                        'images': images,
                                                        'instances': instances,
                                                        'instance_info': instance_info,
                                                        'floating_ips': floating_ips,
                                                        'private_networks': private_networks,
                                                        'public_networks': public_networks,
                                                        'priv_net_list':priv_net_list,
                                                        'pub_net_list':pub_net_list,
                                                        'flavors': flavors
                                                        }))

def user_view(request, project_name, project_id, user_name):
    auth = request.session['auth']
    uo = user_ops(auth)
    user_dict = {'username': user_name, 'project_name': project_name}
    user_info = uo.get_user_info(user_dict)

    return render_to_response('coal/user_view.html',
                               RequestContext(request, {'project_name': project_name,
                                                        'current_project_id': project_id,
                                                        'user_info': user_info,
                                                 }))

def key_view(request, sec_key_id, project_id):
    auth = request.session['auth']
    so = server_ops(auth)
    key_dict = {'sec_key_id': sec_key_id, 'project_id': project_id}
    key_info = so.get_sec_keys(key_dict)

    return render_to_response('coal/key_view.html',
                               RequestContext(request, {
                                                        'key_info': key_info,
                                                        'current_project_id': project_id
                                                        }))


def key_delete(request, sec_key_name, project_id):

    try:
        auth = request.session['auth']
        so = server_ops(auth)
        key_dict = {'sec_key_name': sec_key_name, 'project_id': project_id}
        out = so.delete_sec_keys(key_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to delete key pair.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    
    return render_to_response('coal/key_view.html',
                               RequestContext(request, {
                                                        'key_info': key_info,
                                                        'project_id': project_id
                                                        }))



def download_public_key(request, sec_key_id, sec_key_name, project_id):
    auth = request.session['auth']
    so = server_ops(auth)
    key_dict = {'sec_key_id': sec_key_id, 'project_id': project_id}
    key_info = so.get_sec_keys(key_dict)
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename="%s.pem"' % sec_key_name
    response.write(key_info['public_key'])
    return response

def attach_server_to_network(request, server_id, project_id, net_id):
    auth = request.session['auth']
    so = server_ops(auth)

    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    return HttpResponseRedirect(redirect_to)

def volume_view(request, project_id, volume_id):
    auth = request.session['auth']
    vo = volume_ops(auth)
    sno = snapshot_ops(auth)
    so = server_ops(auth)
    instances = so.list_servers(project_id)
    snapshots = sno.list_snapshots()
    vol_dict = {'project_id': project_id, 'volume_id': volume_id}
    volume_info = vo.get_volume_info(vol_dict)
    attached_to = None
    if volume_info['volume_instance']:
        server_dict = {'project_id': project_id, 'server_id': volume_info['volume_instance']}
        attached_to = so.get_server(server_dict)

    return render_to_response('coal/volume_view.html',
                               RequestContext(request, {'current_project_id' : project_id,
                                                        'volume_info': volume_info,
                                                        'snapshots': snapshots,
                                                        'attached_to': attached_to,
                                                        'instances': instances,
                                                        }))

def floating_ip_view(request, floating_ip_id):
    auth = request.session['auth']
    l3o = layer_three_ops(auth)
    fip = l3o.get_floating_ip(floating_ip_id)
    so = server_ops(auth)
    instances = so.list_servers(fip['project_id'])

    return render_to_response('coal/floating_ip_view.html',
                               RequestContext(request, {
                                                        'fip': fip,
                                                        'instances': instances,
                                                 }))

def create_user(request, username, password, user_role, email, project_id):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'password':password, 'user_role':user_role, 'email': email, 'project_id': project_id}
        newuser= uo.create_user(user_dict)
        redirect_to = "/projects/%s/view/" % ("CHANGEME") #<<<<<<<<<< This doesn't work
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to create user.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
        return HttpResponseRedirect("/projects/manage")
    except:
        messages.warning(request, "Unable to create security group.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def delete_sec_group(request, sec_group_id, project_id):
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        sec_dict = {'sec_group_id': sec_group_id, 'project_id':project_id}
        so.delete_sec_group(sec_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        messages.warning(request, "Unable to delete security group.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_keypair(request, key_name, project_id):
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        key_dict = {'key_name': key_name, 'project_id': project_id}
        newkey= so.create_sec_keys(key_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        response = HttpResponseRedirect(redirect_to)
        return render_to_response(response)
    except:
        messages.warning(request, "Unable to create keypair.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def import_image(request, image_name, container_format, disk_format, image_type, image_location, visibility):
    try:
        auth = request.session['auth']
        go = glance_ops(auth)
        import_dict = {'image_name': image_name, 'container_format': container_format, 'disk_format': disk_format, 'visibility': visibility}
        image_location = image_location.replace("G", "/")
        if image_type == 'local':
            import_dict['image_file'] = image_location
        else:
            import_dict['image_url'] = image_location
        out = go.import_image(import_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except:
        messages.warning(request, "Unable to create volume.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def delete_image(request, image_id):
    try:
        auth = request.session['auth']
        go = glance_ops(auth)
        out = go.delete_image(image_id)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except:
        messages.warning(request, "Unable to create volume.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def create_volume(request, volume_name, volume_size, description, project_id):
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        create_vol = {'volume_name': volume_name, 'volume_size': volume_size, 'description': description, 'project_id': project_id}
        vo.create_volume(create_vol)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except:
        messages.warning(request, "Unable to create volume.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def attach_volume(request, project_id, instance_id, volume_id, mount):
    try:
        mount = mount.replace("&47", "/")
        auth = request.session['auth']
        sso = server_storage_ops(auth)
        attach_vol = {'project_id': project_id, 'instance_id': instance_id, 'volume_id': volume_id, 'mount_point': mount}
        out = sso.attach_vol_to_server(attach_vol)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to create volume.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_snapshot(request, project_id, name, volume_id, desc):
    try:
        auth = request.session['auth']
        sno = snapshot_ops(auth)
        create_snap = {'project_id': project_id, 'snapshot_name': name, 'volume_id': volume_id, 'snapshot_desc': desc}
        out = sno.create_snapshot(create_snap)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to create snapshot.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def delete_snapshot(request, project_id, snapshot_id):
    try:
        auth = request.session['auth']
        sno = snapshot_ops(auth)
        delete_snap = {'project_id': project_id, 'snapshot_id': snapshot_id}
        out = sno.delete_snapshot(delete_snap)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to delete snapshot.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def detach_volume(request, project_id, volume_id):
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        sso = server_storage_ops(auth)
        v_dict = {'volume_id': volume_id, 'project_id': project_id}
        v_info = vo.get_volume_info(v_dict)
        detach_vol = {'project_id': project_id, 'instance_id': v_info['volume_instance'], 'volume_id': volume_id}
        out = sso.detach_vol_from_server(detach_vol)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to create volume.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def delete_volume(request, volume_id, project_id):
    try:
        auth = request.session['auth']
        vo = volume_ops(auth)
        delete_vol = {'volume_id': volume_id, 'project_id': project_id}
        vo.delete_volume(delete_vol)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except:
        messages.warning(request, "Unable to delete volume.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def create_router(request, router_name, priv_net, default_public, project_id):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        no = neutron_net_ops(auth)
        netinfo = no.get_network(priv_net)
        subnet = netinfo["net_subnet_id"][0]['subnet_id']

        create_router = {'router_name': router_name, 'project_id': project_id}
        router = l3o.add_router(create_router)

        add_dict = {'router_id': router['router_id'], 'ext_net_id': default_public, 'project_id': project_id}
        l3o.add_router_gateway_interface(add_dict)

        internal_dict = {'router_id': router['router_id'], 'project_id': project_id, 'subnet_id': subnet}
        l3o.add_router_internal_interface(internal_dict)

        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except:
        messages.warning(request, "Unable to create router.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def delete_router(request, project_id, router_id):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        router=l3o.get_router(router_id)
        proj_rout_dict = {'router_id': router_id, 'project_id': project_id}
        l3o.delete_router_gateway_interface(proj_rout_dict)
        subnet_id=router["router_int_sub_id"]
        if subnet_id:
            remove_dict = {'router_id': router_id, 'subnet_id': subnet_id, 'project_id': project_id}
            l3o.delete_router_internal_interface(remove_dict)
        l3o.delete_router(proj_rout_dict)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except:
        messages.warning(request, "Unable to delete router.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def destroy_project(request, project_id, project_name):
    try:
        auth = request.session['auth']
        proj_dict = {'project_name': project_name, 'project_id': project_id, 'keep_users': False}
        destroy.destroy_project(auth, proj_dict)
        return HttpResponseRedirect('/')

    except:
        messages.warning(request, "Unable to destroy project.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def allocate_floating_ip(request, project_id, ext_net_id):
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        input_dict = {'ext_net_id': ext_net_id, 'project_id': project_id}
        l3o.allocate_floating_ip(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to allocate IP.  The IP range may be used up.")
        return HttpResponseRedirect(redirect_to)

def deallocate_floating_ip(request, project_id, floating_ip):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        input_dict = {'floating_ip': floating_ip, 'project_id': project_id}
        l3o.deallocate_floating_ip(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to deallocate floating ip.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def take_snapshot(request, snapshot_name, snapshot_desc, volume_id, project_id):
    try:
        auth = request.session['auth']
        sno = snapshot_ops(auth)
        create_snap = {'snapshot_name': snapshot_name, 'snapshot_desc': snapshot_desc, 'volume_id': volume_id, 'project_id': project_id}
        sno.create_snapshot(create_snap)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to take snapshots.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_image(request, name, sec_group_name, avail_zone, flavor_name, sec_key_name, image_name, network_name, project_id):
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        no = neutron_net_ops(auth)
        instance = {    'project_id':project_id, 'sec_group_name':sec_group_name,
                        'avail_zone':avail_zone, 'sec_key_name': sec_key_name,
                        'network_name': network_name,'image_name': image_name,
                        'flavor_name':flavor_name, 'name':name}
        server = so.create_server(instance)
        priv_net_list = no.list_internal_networks(project_id)
        default_priv = priv_net_list[0]['net_id']
        input_dict = {'server_id':server.server_id, 'net_id': default_priv, 'project_id': project_id}
        net_info = so.attach_server_to_network(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to create image.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def pause_server(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'instance_id':instance_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        saa.pause_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to pause server.")
        return HttpResponseRedirect(redirect_to)

def unpause_server(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'instance_id':instance_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        saa.unpause_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to unpause server.")
        return HttpResponseRedirect(redirect_to)

def suspend_server(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'instance_id':instance_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        saa.suspend_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to suspend server.")
        return HttpResponseRedirect(redirect_to)

def resume_server(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'instance_id':instance_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        saa.resume_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to resume server.")
        return HttpResponseRedirect(redirect_to)

def delete_server(request, project_id, server_id):
    input_dict = {'project_id':project_id, 'server_id':server_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        so = server_ops(auth)
        so.delete_server(input_dict)
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to delete instance.")
        return HttpResponseRedirect(redirect_to)

def resize_server(request, project_id, instance_id, flavor_id):
    input_dict = {'project_id':project_id, 'server_id':instance_id, 'flavor_id': flavor_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        sa = server_actions(auth)
        #import pdb; pdb.set_trace()
        sa.resize_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to resize server.")
        return HttpResponseRedirect(redirect_to)

def confirm_resize(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'instance_id':instance_id}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        sa = server_actions(auth)
        sa.confirm_resize(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to confirm resize.")
        return HttpResponseRedirect(redirect_to)

def reboot(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'server_id':instance_id, 'action_type':"SOFT"}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        sa = server_actions(auth)
        out = sa.reboot_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to reboot server.")
        return HttpResponseRedirect(redirect_to)

def power_cycle(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'server_id':instance_id, 'action_type':"HARD"}
    referer = request.META.get('HTTP_REFERER', None)
    redirect_to = urlsplit(referer, 'http', False)[2]
    try:
        auth = request.session['auth']
        sa = server_actions(auth)
        sa.reboot_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to power cycle server.")
        return HttpResponseRedirect(redirect_to)

def live_migrate_server(request, project_id, instance_id, host_name):
    input_dict = {'project_id':project_id, 'instance_id':instance_id, 'openstack_host_id':host_name}
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        out = ssa.live_migrate_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to live migrate server.")
        return HttpResponseRedirect(redirect_to)

def migrate_server(request, project_id, instance_id):
    input_dict = {'project_id':project_id, 'instance_id':instance_id}
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        out = ssa.migrate_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to migrate server.")
        return HttpResponseRedirect(redirect_to)

def evacuate_server(request, project_id, instance_id, host_name):
    input_dict = {'project_id':project_id, 'instance_id':instance_id, 'openstack_host_id':host_name}
    try:
        auth = request.session['auth']
        saa = server_admin_actions(auth)
        out = ssa.evacuate_server(input_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to evacuate server.")
        return HttpResponseRedirect(redirect_to)

def assign_floating_ip(request, floating_ip, instance_id, project_id):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        update_dict = {'floating_ip':floating_ip, 'instance_id':instance_id, 'project_id':project_id, 'action': 'add'}
        out = l3o.update_floating_ip(update_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to assign floating ip.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 

def unassign_floating_ip(request, floating_ip_id):
    try:
        auth = request.session['auth']
        l3o = layer_three_ops(auth)
        ip = l3o.get_floating_ip(floating_ip_id)
        update_dict = {'floating_ip':ip['floating_ip'], 'instance_id':ip['instance_id'], 'project_id':ip['project_id'], 'action': 'remove'}
        l3o.update_floating_ip(update_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)
    except:
        messages.warning(request, "Unable to assign floating ip.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
        messages.warning(request, "Unable to toggle user.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def delete_user(request, username, userid):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'user_id':userid}
        out = uo.delete_user(user_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        messages.warning(request, "Unable to delete user.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
        messages.warning(request, "Unable to remove user from project.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def add_existing_user(request, username, user_role, project_id):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        user_dict = {'username': username, 'user_role':user_role, 'project_id': project_id}
        uo.add_user_to_project(user_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        messages.warning(request, "Unable to add existing user.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def update_user_password(request, user_id, project_id, password):
    try:
        auth = request.session['auth']
        uo = user_ops(auth)
        passwd_dict = {'user_id': user_id, 'project_id':project_id, 'new_password': password }
        uo.update_user_password(passwd_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        messages.warning(request, 'Password updated.')
        return HttpResponseRedirect('/')

    except:
        messages.warning(request, "Unable to update user password.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def network_view(request, net_id):
    auth = request.session['auth']
    no = neutron_net_ops(auth)
    nw = no.get_network(net_id)
    sn = no.get_net_subnet(nw['net_subnet_id'][0]['subnet_id'])

    return render_to_response('coal/network_view.html',
                               RequestContext(request, {
                                                        'nw': nw,
                                                        'sn': sn,
                                                        }))

def router_view(request, router_id):
    auth = request.session['auth']
    l3o = layer_three_ops(auth)
    router = l3o.get_router(router_id)

    return render_to_response('coal/router_view.html',
                               RequestContext(request, {
                                                        'router': router,
                                                        }))

def instance_view(request, project_id, server_id):
    auth = request.session['auth']
    so = server_ops(auth)
    fo = flavor_ops(auth)
    i_dict = {'server_id': server_id, 'project_id': project_id}
    server = so.get_server(i_dict)
    flavors = fo.list_flavors()

    return render_to_response('coal/instance_view.html',
                               RequestContext(request, {
                                                        'server': server,
                                                        'flavors': flavors,
                                                        'current_project_id': project_id,
                                                        }))

def add_private_network(request, net_name, admin_state, shared, project_id):
    try:
        auth = request.session['auth']
        no = neutron_net_ops(auth)
        create_dict = {"net_name": net_name, "admin_state": admin_state, "shared": shared, "project_id": project_id}
        network = no.add_private_network(create_dict)
        subnet_dict={"net_id": network['net_id'], "subnet_dhcp_enable": "true", "subnet_dns": ["8.8.8.8"]}
        subnet = no.add_net_subnet(subnet_dict)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    except:
        messages.warning(request, "Unable to add private network.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_private_network(request, project_id, net_id):
    try:
        auth    = request.session['auth']
        no      = neutron_net_ops(auth)
        l3o     = layer_three_ops(auth)
        network = no.get_network(net_id)
        subnets = network['net_subnet_id']

        for subnet in subnets:
            subnet_id = subnet['subnet_id']
            sub_proj_dict = {'net_id': net_id, 'subnet_id': subnet_id, 'project_id': project_id}
            if network['router_id']:
                remove_dict = {'router_id': network['router_id'], 'subnet_id': subnet_id, 'project_id': project_id}
                l3o.delete_router_internal_interface(remove_dict)
            #ports = no.list_net_ports(sub_proj_dict)
                #for port in ports:
                #remove_port_dict = {'subnet_id': subnet_id, 'project_id': project_id, 'port_id': port['port_id']}
                #no.remove_net_port(remove_port_dict)
            no.remove_net_subnet(sub_proj_dict)

        remove_dict={'net_id': net_id, 'project_id': project_id }
        no.remove_network(remove_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        messages.warning(request, "Unable to remove private network.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def create_container(request, name, project_id):
    try:
        auth = request.session['auth']
        cso = container_service_ops(auth)
        create_dict = {"container_name": name, "project_id": project_id}
        out = cso.create_container(create_dict)
        referer = request.META.get('HTTP_REFERER', None)
        redirect_to = urlsplit(referer, 'http', False)[2]
        return HttpResponseRedirect(redirect_to)

    except:
        messages.warning(request, "Unable to add private network.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def setup(request):
    if request.method == 'POST':
        if request.POST.get('cancel'):
            return HttpResponseRedirect('/')
        form = SetupForm(request.POST)
        if form.is_valid():
            management_ip          = form.cleaned_data['management_ip']
            uplink_ip              = form.cleaned_data['uplink_ip']
            vm_ip_min              = form.cleaned_data['vm_ip_min']
            vm_ip_max              = form.cleaned_data['vm_ip_max']
            uplink_dns             = form.cleaned_data['uplink_dns']
            uplink_gateway         = form.cleaned_data['uplink_gateway']
            uplink_domain_name     = form.cleaned_data['uplink_domain_name']
            uplink_subnet      = form.cleaned_data['uplink_subnet']
            mgmt_domain_name       = form.cleaned_data['mgmt_domain_name']
            mgmt_subnet            = form.cleaned_data['mgmt_subnet']
            mgmt_dns               = form.cleaned_data['mgmt_dns']
            #cloud_name             = form.cleaned_data['cloud_name']
            single_node            = form.cleaned_data['single_node']
            admin_password         = form.cleaned_data['admin_password']
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
            return render_to_response('coal/setup_results.html', RequestContext(request, {'management_ip': management_ip}))
        else:
            return render_to_response('coal/setup.html', RequestContext(request, { 'form':form, }))
    else:
        form = SetupForm()
    return render_to_response('coal/setup.html', RequestContext(request, { 'form':form, }))

def build_project(request):
    if request.method == 'POST':
        if request.POST.get('cancel'):
            return HttpResponseRedirect('/')
        form = BuildProjectForm(request.POST)
        if form.is_valid():
            proj_name        = form.cleaned_data['proj_name']
            username         = form.cleaned_data['username']
            password         = form.cleaned_data['password']
            password_confirm = form.cleaned_data['password_confirm']
            email           = form.cleaned_data['email']
            net_name        = form.cleaned_data['net_name']
            subnet_dns      = form.cleaned_data['subnet_dns']
            #ports[] - op
            group_name      = form.cleaned_data['group_name']
            group_desc      = form.cleaned_data['group_desc']
            sec_keys_name   = form.cleaned_data['sec_keys_name']
            router_name     = form.cleaned_data['router_name']

            auth = request.session['auth']
            project_var_array = {'project_name': proj_name,
                                 'user_dict': { 'username': username,
                                                'password': password,
                                                'user_role': 'pu',
                                                'email': email,
                                                'project_id': ''},

                                 'net_name':net_name,
                                 'subnet_dns': subnet_dns,
                                 'sec_group_dict':  { 'ports': '',
                                                     'group_name': group_name,
                                                     'group_desc': 'group_desc',
                                                     'project_id': ''},

                                 'sec_keys_name': sec_keys_name,
                                 'router_name': router_name
                            }
            pid = bcp.build_project(auth, project_var_array)

            redirect_to = "/projects/%s/view/" % (pid)
            return HttpResponseRedirect(redirect_to)

        else:
            return render_to_response('coal/build_project.html', RequestContext(request, { 'form':form, }))

    else:
        form = BuildProjectForm()
    return render_to_response('coal/build_project.html', RequestContext(request, { 'form':form, }))


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
            try:
                user = form.cleaned_data['username']
                pw = form.cleaned_data['password']
                a = authorization(user, pw)
                auth = a.get_auth()
                if auth['token'] == None:
                    form = authentication_form()
                    messages.warning(request, 'Login failed.  Please verify your username and password.')
                    return render_to_response('coal/login.html', RequestContext(request, { 'form':form, }))
                request.session['auth'] = auth
                return render_to_response('coal/welcome.html', RequestContext(request, {  }))
            except:
                form = authentication_form()
                messages.warning(request, 'Login failed.  Please verify your username and password.')
                return render_to_response('coal/login.html', RequestContext(request, { 'form':form, }))
        else:
                form = authentication_form()
                messages.warning(request, 'Login failed.  Please verify your username and password.')
                return render_to_response('coal/login.html', RequestContext(request, { 'form':form, }))
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


# base
import ast, json, sys
# flask
from flask import Flask, jsonify, abort, make_response, request
from werkzeug.exceptions import HTTPException
from flasgger import Swagger
# common
from transcirrus.common import util
from transcirrus.common.auth import authorization
from transcirrus.common import extras
# version
from transcirrus.common import version 
# projects
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.operations import build_complete_project
# instances, security groups and security keys
from transcirrus.component.nova.server import server_ops
from transcirrus.operations import boot_new_instance as boot_from_vol_ops
# flavors
from transcirrus.component.nova.flavor import flavor_ops
# floating ips, routers
from transcirrus.component.neutron.layer_three import layer_three_ops
# volumes
from transcirrus.component.cinder.cinder_volume import volume_ops
from transcirrus.component.nova.storage import server_storage_ops
from transcirrus.component.cinder.cinder_snapshot import snapshot_ops
# networks
from transcirrus.component.neutron.network import neutron_net_ops
# users
from transcirrus.component.keystone.keystone_users import user_ops
# images
from transcirrus.component.glance.glance_ops_v2 import glance_ops


# --- API Setup ----

app = Flask(__name__)
Swagger(app)
node_id = util.get_node_id()
api_ip = util.get_system_variables(node_id)['MGMT_IP']


# --- Error Handlers ----

# 400, bad request
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': {'message': error.description, 'number': 400}}), 400)


# 401, not authorized
@app.errorhandler(401)
def not_authorized(error):
    return make_response(jsonify({'error': {'message': error.description, 'number': 401}}), 401)


# 404, not found
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': {'message': error.description, 'number': 404}}), 404)


# 409, confict
@app.errorhandler(409)
def confict(error):
    return make_response(jsonify({'error': {'message': error.description, 'number': 409}}), 409)


# 500, internal server error
@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': {'message': error.description, 'number': 500}}), 500)


# --- Version Info ----

# get
@app.route('/v1.0/version', methods=['GET'])
def get_version():
    """
    Gets version information.
    ---
    tags:
      - version
    responses:
        200:
            description: Version found.
            schema:
                type: object
                id: VersionDetails
                required:
                  - major
                  - minor
                  - release
                  - full
                  - short
                properties:
                    major:
                        type: integer
                        description: Major version number
                        default: 2
                    minor:
                        type: integer
                        description: Minor version number
                        default: 3
                    release:
                        type: integer
                        description: Release version number
                        default: 1
                    full:
                        type: string
                        description: Fully qualified version number, (major.minor-relase)
                        default: 2.3-1
                    short:
                        type: string
                        description: Short version number, (major.minor)
                        default: 2.3
        500:
            description: Internal server error.
    """
    try:
        version_info = {}
        version_info['major']   = int(version.VERSION_MAJOR)
        version_info['minor']   = int(version.VERSION_MINOR)
        version_info['release'] = int(version.VERSION_RELEASE)
        version_info['full']    = version.VERSION_FULL_STR
        version_info['short']   = version.VERSION_SHORT_STR
        return jsonify({'version': version_info})
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred getting version details.' %(fe))


# --- Projects ----

# get all
@app.route('/v1.0/projects', methods=['GET'])
def get_projects():
    """
    Lists all projects.
    Only returns projects to which the requesting user has access.
    ---
    tags:
      - projects
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
    responses:
        200:
            description: Projects listed.
            schema:
                type: array
                id: Projects
                items:
                    schema:
                        type: object
                        id: Project
                        required:
                          - name
                          - id
                        properties:
                            name:
                                type: string
                                description: name of project
                                default: Project_1
                            id:
                                type: string
                                description: ID of project
                                default: abcd12e3f456789012345a678b9cde01
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        to = tenant_ops(auth)
        projects = []
        # admins can list all projects
        if auth['is_admin'] == 1:
            projects_info = to.list_all_tenants()
        # otherwise list user's own project
        else:
            projects_info = [to.get_tenant(auth['project_id'])]
        # normalize output
        for info in projects_info:
            project =   {
                            'name': info['project_name'],
                            'id':   info['project_id']
                        }
            projects.append(project)
        # remove trans_default
        projects[:] = [p for p in projects if p.get('name') != "trans_default"]
        return jsonify({'projects': projects})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred listing projects.' %(fe))


# get
@app.route('/v1.0/projects/<string:project_id>', methods=['GET'])
def get_project(project_id):
    """
    Gets detailed information about a specified project by ID.
    Only returns project information to which the requesting user has access.
    ---
    tags:
      - projects
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
    responses:
        200:
            description: Project found.
            schema:
                type: object
                id: ProjectDetails
                required:
                    - name
                    - id
                    - security_key_name
                    - security_key_id
                    - security_group_name
                    - security_group_id
                    - host_system_name
                    - host_system_ip
                    - network_name
                    - network_id
                    - is_default
                properties:
                    name:
                        type: string
                        description: name of project
                        default: Project_1
                    id:
                        type: string
                        description: ID of project
                        default: abcd12e3f456789012345a678b9cde01
                    security_key_name:
                        type: string
                        description: name of default security key
                        default: Security_Key_1
                    security_key_id:
                        type: string
                        description: ID of default security key
                        default: a1:23:45:b6:78:90:12:34:5c:d6:e7:fa:bc:de:fa:89
                    security_group_name:
                        type: string
                        description: name of default security group
                        default: Security_Group_1
                    security_group_id:
                        type: string
                        description: ID of default security group
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    host_system_name:
                        type: string
                        description: name of host system
                        default: transcirrus-core
                    host_system_ip:
                        type: string
                        description: IP address of host system
                        default: 127.0.0.1
                    network_name:
                        type: string
                        description: name of default network
                        default: Network_1
                    network_id:
                        type: string
                        description: ID of default network
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    is_default:
                        type: string
                        description: third party authentication default type
                        default: LDAP
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        # check project_id
        project_info = validate_project(project_id, auth)
        # normalize output
        project = {
                        'name':                     project_info['project_name'],
                        'id':                       project_info['project_id'],
                        'security_key_name':        project_info['def_security_key_name'],
                        'security_key_id':          project_info['def_security_key_id'],
                        'security_group_name':      project_info['def_security_group_name'],
                        'security_group_id':        project_info['def_security_group_id'],
                        'host_system_name':         project_info['host_system_name'],
                        'host_system_ip':           project_info['host_system_ip'],
                        'network_name':             project_info['def_network_name'],
                        'network_id':               project_info['def_network_id'],
                        'is_default':               project_info['is_default']
                   }
        return jsonify({'project': project})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred getting details for project %s.' %(fe, project_id))


# create
@app.route('/v1.0/projects', methods=['POST'])
def create_project():
    """
    Creates a specified project.
    Only available to admins.
    ---
    tags:
      - projects
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_parameters
        in: body
        description: parameters for project creation
        required: true
        schema:
            id: ProjectParameters
            type: object
            required:
              - name
              - admin_username
              - admin_password
              - admin_email
              - security_group_name
              - security_key_name
              - network_name
              - router_name
              - dns_address
            properties:
                name:
                    type: string
                    description: name for project
                    default: Project_1
                username:
                    type: string
                    description: username for project admin
                    default: Admin_Project_1
                password:
                    type: string
                    description: password for project admin
                    default: password
                email:
                    type: string
                    description: email for project admin
                    default: admin_project_1@email.com
                security_group_name:
                    type: string
                    description: name for project's default security group
                    default: Security_Group_1
                security_key_name:
                    type: string
                    description: name for project's default security key
                    default: Security_Key_1
                network_name:
                    type: string
                    description: name for project's default network
                    default: Network_1
                router_name:
                    type: string
                    description: name for project's default router
                    default: Router_1
                dns_address:
                    type: string
                    description: subnet DNS address for project
                    default: 8.8.8.8
    responses:
        200:
            description: Project created.
            schema:
                id: ProjectCreated
                type: object
                required:
                  - name
                  - id
                properties:
                    name:
                        type: string
                        description: name of project
                        default: Project_1
                    id:
                        type: string
                        description: ID of project
                        default: abcd12e3f456789012345a678b9cde01
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        # check is_admin
        if auth['is_admin'] != 1:
            abort(401, 'Not authroized. Only admins can create projects.')
        try:
            data = request.get_data()
            json_data = json.loads(data)
        except:
            abort(400, 'Bad request. Body must be in JSON format.')
        project_create = {}
        user_dict = {}
        sec_group_dict = {}
        dns_address = []
        project_create['user_dict'] = user_dict
        project_create['sec_group_dict'] = sec_group_dict
        # required
        try:
            # project info
            project_create['project_name'] = json_data['name']
            project_create['net_name'] = json_data['network_name']
            project_create['subnet_dns'] = dns_address.append(json_data['dns_address'])
            project_create['sec_keys_name'] = json_data['security_key_name']
            project_create['router_name'] = json_data['router_name']
            # user info
            user_dict['username'] = json_data['username']
            user_dict['password'] = json_data['password']
            user_dict['email'] = json_data['email']
            user_dict['user_role'] = "admin"
            user_dict['project_id'] = ""
            # security info
            sec_group_dict['group_name'] = json_data['security_group_name']
            sec_group_dict['ports'] = ""
            sec_group_dict['group_desc'] = "none"
            sec_group_dict['project_id'] = ""
        except:
            abort(400, 'Bad request. Body must contain name, network_name, dns_address, router_name, username, password, email, security_group_name, and security_key_name.')
        project_info = build_complete_project.build_project(auth, project_create)
        # normalize output
        project =   {
                        'name': project_create['project_name'],
                        'id':   project_info
                    }
        return jsonify({'project': project})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred creating project.' %(fe))


# --- Instances ----

# get all in cloud
@app.route('/v1.0/instances', methods=['GET'])
def get_all_instances():
    """
    Lists all instances.
    Only returns instances to which the requesting user has access.
    ---
    tags:
      - instances
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
    responses:
        200:
            description: Instances listed.
            schema:
                type: array
                id: Instances
                items:
                    schema:
                        type: object
                        id: Instance
                        required:
                            - name
                            - id
                            - project_id
                            - floating_ip
                            - status
                            - zone
                        properties:
                            name:
                                type: string
                                description: name of instance
                                default: Instance_1
                            id:
                                type: string
                                description: ID of instance
                                default: 1234a56b-8901-2345-67c8-90de12f34ab5
                            project_id:
                                type: string
                                description: ID of project
                                default: abcd12e3f456789012345a678b9cde01
                            floating_ip:
                                type: string
                                description: floating IP address of instance
                                default: 127.0.0.1
                            status:
                                type: string
                                description: status of instance
                                default: ACTIVE
                            zone:
                                type: string
                                description: availability zone of instance
                                default: nova
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        so = server_ops(auth)
        instances = []
        # admins can list all intances
        if auth['is_admin'] == 1:
            instances_info = so.list_all_servers()
        # otherwise list all user has access to
        else:
            instances_info = so.list_servers()
        # normalize output
        for info in instances_info:
            instance =  {
                            "project_id":   info['project_id'],
                            "floating_ip":  info['public_ip'],
                            "id":           info['server_id'],
                            "name":         info['server_name'],
                            "status":       info['status'],
                            "zone":         info['zone']
                        }
            instances.append(instance)
        return jsonify({'instances': instances})
    except HTTPException as he:
        raise he
    except:
        abort(500, 'Internal error. Error <%s> occurred listing instances.' %(fe))


# get all in project
@app.route('/v1.0/<string:project_id>/instances', methods=['GET'])
def get_instances(project_id):
    """
    Lists all instances in specified project by ID.
    Only returns instances to which the requesting user has access.
    ---
    tags:
      - instances
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
    responses:
        200:
            description: Instances listed.
            schema:
                type: array
                id: Instances
                items:
                    schema:
                        type: object
                        id: Instance
        400:
            description: Bad request.
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        so = server_ops(auth)
        # check project_id
        validate_project(project_id, auth)
        instances = []
        instances_info = so.list_servers(project_id)
        # normalize output
        for instance in instances_info:
            instance =  {
                            "project_id":   instance['project_id'],
                            "floating_ip":  instance['public_ip'],
                            "id":           instance['server_id'],
                            "name":         instance['server_name'],
                            "status":       instance['status'],
                            "zone":         instance['zone']
                        }
            instances.append(instance)
        return jsonify({'instances': instances})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred listing instances in project %s.' %(fe, project_id))


# get
@app.route('/v1.0/<string:project_id>/instances/<string:instance_id>', methods=['GET'])
def get_instance(project_id, instance_id):
    """
    Gets detailed information about a specified instance by ID.
    Only returns project information to which the requesting user has access.
    ---
    tags:
      - instances
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: instance_id
        in: path
        type: string
        required: true
        description: ID of target instance
    responses:
        200:
            description: Instance found.
            schema:
                type: object
                id: InstanceDetails
                required:
                    - name
                    - id
                    - project_id
                    - security_key_name
                    - security_group_name
                    - specification_name
                    - specification_id
                    - os
                    - external_network_id
                    - network_info
                    - zone
                    - status
                    - state
                    - physical_node_id
                    - floating_ip
                    - floating_ip_id
                    - novnc_console
                    - date_created
                    - is_boot_from_volume
                    - fault
                properties:
                    name:
                        type: string
                        description: name of instance
                        default: Instance_1
                    id:
                        type: string
                        description: ID of instance
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    project_id:
                        type: string
                        description: ID of instance's project
                        default: abcd12e3f456789012345a678b9cde01
                    security_key_name:
                        type: string
                        description: name of instance's security key
                        default: Security_Key_1
                    security_group_name:
                        type: string
                        description: name of instance's security group
                        default: Security_Group_1
                    specification_name:
                        type: string
                        description: name of instance's specification
                        default: m1.tiny
                    specification_id:
                        type: string
                        description: ID of instance's specification
                        default: "12345"
                    os:
                        type: string
                        description: OS of instance
                        default: CentOS-65-x86_64
                    network_info:
                        type: object
                        description: network information of instance
                        schema:
                            type: object
                            id: NetworkInfo
                            required:
                              - internal
                              - external
                            properties:
                                internal:
                                    type: array
                                    id: InstanceInternalNetworks
                                    items:
                                        schema:
                                            type: object
                                            id: InstanceInternalNetwork
                                            required:
                                              - name
                                              - id
                                              - OS-EXT-IPS-MAC:mac_addr
                                              - OS-EXT-IPS:type
                                              - addr
                                              - version
                                            properties:
                                                name:
                                                    type: string
                                                    description: name of network
                                                    default: Network_1
                                                id:
                                                    type: string
                                                    description: ID of network
                                                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
                                                OS-EXT-IPS-MAC:mac_addr:
                                                    type: string
                                                    description: mac address of network port
                                                    default: ab:12:3c:4d:ef:5a
                                                OS-EXT-IPS:type:
                                                    type: string
                                                    description: address type
                                                    default: fixed
                                                addr:
                                                    type: string
                                                    description: IP address of instance
                                                    default: 10.0.1.7
                                                version:
                                                    type: integer
                                                    description: ip version
                                                    default: 4
                                external:
                                    type: array
                                    id: InstanceExternalNetworks
                                    items:
                                        schema:
                                            type: object
                                            id: InstanceExternalNetwork
                                            required:
                                              - name
                                              - id
                                              - OS-EXT-IPS-MAC:mac_addr
                                              - OS-EXT-IPS:type
                                              - addr
                                              - version
                                            properties:
                                                name:
                                                    type: string
                                                    description: name of network
                                                    default: Network_1
                                                id:
                                                    type: string
                                                    description: ID of network
                                                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
                                                OS-EXT-IPS-MAC:mac_addr:
                                                    type: string
                                                    description: mac address of network port
                                                    default: ab:12:3c:4d:ef:5a
                                                OS-EXT-IPS:type:
                                                    type: string
                                                    description: address type
                                                    default: floating
                                                addr:
                                                    type: string
                                                    description: IP address of instance
                                                    default: 10.0.1.7
                                                version:
                                                    type: integer
                                                    description: ip version
                                                    default: 4
                    zone:
                        type: string
                        description: availability zone of instance
                        default: nova
                    status:
                        type: string
                        description: status of instance
                        default: ACTIVE
                    state:
                        type: string
                        description: state of instance
                        default: active
                    physical_node_id:
                        type: string
                        description: ID of physical node hosting instance
                        default: abc1def2ab34567890cd12ef34abc56d789012ef3456a78901bc2de3
                    floating_ip:
                        type: string
                        description: floating IP address of instance
                        default: 127.0.0.1
                    floating_ip_id:
                        type: string
                        description: ID of instance's floating IP address
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    novnc_console:
                        type: string
                        description: url of instance's novnc console
                        default: http://127.0.0.1:6080/vnc_auto.html?token=1234a56b-8901-2345-67c8-90de12f34ab5
                    date_created:
                        type: string
                        description: date of instance creation
                        default: "2015-10-02T19:28:33Z"
                    is_boot_from_volume:
                        type: boolean
                        description: conveying if instance boots from volume
                        default: false
                    fault:
                        type: string
                        description: fault of instance
                        default: None
        400:
            description: Bad request.
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        nno = neutron_net_ops(auth)
        # check project_id
        validate_project(project_id, auth)
        # check instance_id
        instance_info = validate_instance(instance_id, project_id, auth)
        internal = []
        external = []
        # get instance's network info
        net_id = instance_info['server_net_id']
        net_name = nno.get_network(net_id)['net_name']
        # normalize output
        for info in instance_info['server_int_net'][net_name]:
            if info['OS-EXT-IPS:type'] == "fixed":
                info['name'] = net_name
                info['id'] = net_id
                internal.append(info)
            elif info['OS-EXT-IPS:type'] == "floating":
                info['name'] = net_name
                info['id'] = net_id
                external.append(info)
        if 'boot_from_vol' in instance_info and instance_info['boot_from_vol'] == "true":
            instance_info['boot_from_vol'] = True
        else:
            instance_info['boot_from_vol'] = False
        instance = {
                        'name':                 instance_info['server_name'],
                        'id':                   instance_info['server_id'],
                        'project_id':           instance_info['project_id'],
                        'security_key_name':    instance_info['server_key_name'],
                        'security_group_name':  instance_info['server_group_name'],
                        'specification_id':     instance_info['flavor_id'],
                        'specification_name':   instance_info['server_flavor'],
                        'os':                   instance_info['server_os'],
                        'network_info':         {
                                                    'internal': internal,
                                                    'external': external
                                                },
                        'zone':                 instance_info['server_zone'],
                        'status':               instance_info['server_status'],
                        'state':                instance_info['server_state'],
                        'physical_node_id':     instance_info['server_node'],
                        'floating_ip_id':       instance_info['floating_ip_id'],
                        'floating_ip':          instance_info['server_public_ips'],
                        'novnc_console':        instance_info['novnc_console'],
                        'date_created':         instance_info['date_created'],
                        'is_boot_from_volume':  instance_info['boot_from_vol']
                   }
        return jsonify({'instance': instance})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred getting details for instance %s.' %(fe, instance_id))


# create
@app.route('/v1.0/<string:project_id>/instances', methods=['POST'])
def create_instance(project_id):
    """
    Creates a specified instance.
    ---
    tags:
      - instances
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: instance_parameters
        in: body
        description: parameters for instance creation
        required: true
        schema:
            id: InstanceParameters
            type: object
            required:
              - name
              - image_id
              - specification_id
              - security_group_name
              - security_key_name
            properties:
                name:
                    type: string
                    description: name for instance
                    default: Instance_1
                image_id:
                    type: string
                    description: ID of image for instance
                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
                specification_id:
                    type: string
                    description: ID of specification for instance
                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
                security_group_name:
                    type: string
                    description: name of security group for instance, uses project default if not specified
                    default: Security_Group_1
                security_key_name:
                    type: string
                    description: name of security key for instance, uses project default if not specified
                    default: Security_Key_1
                network_name:
                    type: string
                    description: name of network for instance, uses project default if not specified
                    default: Network_1
                zone:
                    type: string
                    description: availability zone for instance, uses nova is not specified
                    default: nova
                is_boot_from_volume:
                    type: boolean
                    description: conveying if instance boots from volume desired, false if not specified
                    default: false
                volume_size:
                    type: integer
                    description: size for boot volume in GB, uses minimum size to satisfy specification if not specified and boot_from volume is true
                    default: 10
                volume_name:
                    type: string
                    description: name for boot volume, uses generic name if not specified and boot_from volume is true
                    default: Boot_Volume_1
                volume_type:
                    type: string
                    description: type for boot volume, either spindle or ssd, uses spindle if not specified and boot_from volume is true
                    default: spindle
    responses:
        200:
            description: Instance created.
            schema:
                id: InstanceCreated
                type: object
                required:
                  - name
                  - id
                  - security_key_name
                  - security_group_name
                  - project_id
                  - username
                properties:
                    name:
                        type: string
                        description: name of instance
                        default: Instance_1
                    id:
                        type: string
                        description: ID of instance
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    security_key_name:
                        type: string
                        description: name of instance's security key
                        default: Security_Key_1
                    security_group_name:
                        type: string
                        description: name of instance's security group
                        default: Security_Group_1
                    project_id:
                        type: string
                        description: ID of instance's project
                        default: abcd12e3f456789012345a678b9cde01
                    username:
                        type: string
                        description: name of instance's creator
                        default: User_1
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        try:
            data = request.get_data()
            json_data = json.loads(data)
        except:
            abort(400, 'Bad request. Body must be in JSON format.')
        instance_create = {}
        # required
        try:
            instance_create['project_id'] = project_id
            instance_create['instance_name'] = json_data['name']
            instance_create['image_id'] = json_data['image_id']
            instance_create['flavor_id'] = json_data['specification_id']
            instance_create['sec_group_name'] = json_data['security_group_name']
            instance_create['sec_key_name'] = json_data['security_key_name']
        except:
            abort(400, 'Bad request. Body must contain name, image_id, specification_id, security_group_name and security_key_name.')
        # optional
        if 'network_name' in json_data:
            instance_create['network_name'] = json_data['network_name']
        if 'zone' in json_data:
            instance_create['avail_zone'] = json_data['zone']
        if 'is_boot_from_volume' in json_data:
            instance_create['boot_from_vol'] = json_data['is_boot_from_volume']
        if 'volume_size' in json_data:
            instance_create['volume_size'] = json_data['volume_size']
        if 'volume_name' in json_data:
            instance_create['volume_name'] = json_data['volume_name']
        if 'volume_type' in json_data:
            instance_create['volume_type'] = json_data['volume_type']
        instance_info = boot_from_vol_ops.boot_instance(instance_create, auth)['instance']
        # check instace create success
        if instance_info is not None:
            # normalize output
            instance =  {
                            'name':                 instance_info['vm_name'],
                            'id':                   instance_info['vm_id'],
                            'security_key_name':    instance_info['sec_key_name'],
                            'security_group_name':  instance_info['sec_group_name'],
                            'project_id':           instance_info['project_id'],
                            'username':             instance_info['created_by'],
                        }
            return jsonify({'instance': instance})
        else:
            abort(500, 'Internal error. Unable to create instance.')
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred creating instance.' %(fe))


# delete
@app.route('/v1.0/<string:project_id>/instances/<string:instance_id>', methods=['DELETE'])
def delete_instance(project_id, instance_id):
    """
    Deletes a specified instance by ID.
    Only deletes instance if requesting user has access.
    ---
    tags:
      - instances
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: instance_id
        in: path
        type: string
        required: true
        description: ID of target instance
    responses:
        200:
            description: Instance deleted.
            schema:
                id: ObjectDeleted
                type: object
                required:
                  - id
                properties:
                    id:
                        type: string
                        description: ID of target object
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        so = server_ops(auth)
        # check project_id
        validate_project(project_id, auth)
        # check instance_id
        validate_instance(instance_id, project_id, auth)
        instance_delete =   {
                                'project_id':   project_id,
                                'server_id':    instance_id
                            }
        instance_info = so.delete_server(instance_delete)
        # check instance delete success
        if instance_info == "OK":
            # normalize output
            instance =  {
                            'id':       instance_id
                        }
            return jsonify({'instance': instance})
        else:
            abort(500, 'Internal error. Unable to delete instance.')
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred deleting instance %s.' %(fe, instance_id))


# --- Flavors ----

# create
@app.route('/v1.0/<string:project_id>/instance_specifications', methods=['POST'])
def create_flavor(project_id):
    """
    Creates a specified instance specification.
    ---
    tags:
      - instance specifications
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: instance_specification_parameters
        in: body
        description: parameters for instance specification creation
        required: true
        schema:
            id: InstanceSpecificationParameters
            type: object
            required:
              - name
              - ram
              - disk
              - cpus
            properties:
                name:
                    type: string
                    description: name for instance specification
                    default: Instance_Specification_1
                ram:
                    type: integer
                    description: amount of ram for instance specification in MB
                    default: 1024
                disk:
                    type: integer
                    description: size of disk for instance specification in GB
                    default: 10
                cpus:
                    type: integer
                    description: number of cpus for instance specification
                    default: 2
                visibility:
                    type: string
                    description: public if sharing is desired, else private, uses private is not specified
                    default: private
    responses:
        200:
            description: Instance Specification created.
            schema:
                id: InstanceSpecificationCreated
                type: object
                required:
                  - id
                  - name
                properties:
                    id:
                        type: string
                        description: ID of instance specification
                        default: 12345
                    name:
                        type: string
                        description: name of instance specification
                        default: Instance_Specification_1
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        fo = flavor_ops(auth)
        try:
            data = request.get_data()
            json_data = json.loads(data)
        except:
            abort(400, 'Bad request. Body must be in JSON format.')
        instance_specification_create = {}
        # check project_id
        validate_project(project_id, auth)
        # required
        try:
            instance_specification_create['name'] = json_data['name']
            instance_specification_create['ram'] = json_data['ram']
            instance_specification_create['boot_disk'] = json_data['disk']
            instance_specification_create['cpus'] = json_data['cpus']
        except:
            abort(400, 'Bad request. Body must contain name, ram, disk and cpus.')
        # optional
        if 'visibility' in json_data and json_data['visibility'] == "public":
            instance_specification_create['public'] = "True"
        instance_specification_info = fo.create_flavor(instance_specification_create)
        # check flavor create success
        if instance_specification_info['status'] == "OK":
            # normalize output
            instance_specification =    {
                                            'id':   instance_specification_info['flav_id'],
                                            'name': instance_specification_info['flavor_name']
                                        }
            return jsonify({'instance_specification': instance_specification})
        else:
            abort(500, 'Internal error. Unable to create instance specification.')
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred creating instance specification.' %(fe))


# --- Floating IPs ----

# get all
@app.route('/v1.0/floating_ips', methods=['GET'])
def get_floating_ips():
    """
    Lists all floating IPs.
    Only returns floating IPs to which the requesting user has access.
    ---
    tags:
      - floating ips
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
    responses:
        200:
            description: Floating IPs listed.
            schema:
                type: array
                id: FloatingIPs
                items:
                    schema:
                        type: object
                        id: FloatingIP
                        required:
                          - address
                          - id
                          - is_in_use
                        properties:
                            address:
                                type: string
                                description: address of floating IP
                                default: 127.0.0.1
                            id:
                                type: string
                                description: ID of floating IP
                                default: 1234a56b-8901-2345-67c8-90de12f34ab5
                            is_in_use:
                                type: boolean
                                description: conveying if floating IP is in use
                                default: false
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        l3 = layer_three_ops(auth)
        floating_ips = []
        floating_ips_info = l3.list_floating_ips()
        # normalize output
        for info in floating_ips_info:
            if info['floating_in_use'] == "true":
                info['floating_in_use'] = True
            else:
                info['floating_in_use'] = False
            floating_ip =   {
                                'address':      info['floating_ip'],
                                'id':           info['floating_ip_id'],
                                'is_in_use':    info['floating_in_use']
                            }
            floating_ips.append(floating_ip)
        return jsonify({'floating_ips': floating_ips})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred listing floating IPs.' %(fe))


# get
@app.route('/v1.0/floating_ips/<string:floating_ip_id>', methods=['GET'])
def get_floating_ip(floating_ip_id):
    """
    Gets detailed information about a specified floating IP by ID.
    Only returns floating IP information to which the requesting user has access.
    ---
    tags:
      - floating ips
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: floating_ip_id
        in: path
        type: string
        required: true
        description: ID of target floating IP
    responses:
        200:
            description: Floating IP found.
            schema:
                type: object
                id: FloatingIPDetails
                required:
                    - address
                    - id
                    - instance_name
                    - instance_id
                    - network_name
                    - network_id
                    - project_id
                properties:
                    address:
                        type: string
                        description: address of floating IP
                        default: 127.0.0.1
                    id:
                        type: string
                        description: ID of floating IP
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    instance_name:
                        type: string
                        description: name of instance with which the floating IP is associated
                        default: Instance_1
                    instance_id:
                        type: string
                        description: ID of instance with which the floating IP is associated
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    network_name:
                        type: string
                        description: name of floating IP's internal network
                        default: Network_1
                    network_id:
                        type: string
                        description: ID of floating IP's internal network
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    project_id:
                        type: string
                        description: ID of floating IP's project
                        default: abcd12e3f456789012345a678b9cde01
        400:
            description: Bad request.
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        # check floating_ip_id
        floating_ip_info = validate_floating_ip(floating_ip_id, auth)
        # normalize output
        floating_ip =   {
                            'address':          floating_ip_info['floating_ip'],
                            'id':               floating_ip_info['floating_ip_id'],
                            'instance_name':    floating_ip_info['instance_name'],
                            'instance_id':      floating_ip_info['instance_id'],
                            'network_name':     floating_ip_info['internal_net_name'],
                            'network_id':       floating_ip_info['internal_net_id'],
                            'project_id':       floating_ip_info['project_id'],
                        }
        return jsonify({'floating_ip': floating_ip})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred getting details for floating IP %s.' %(fe, floating_ip_id))


# create
@app.route('/v1.0/floating_ips', methods=['POST'])
def create_floating_ip():
    """
    Creates a floating IP address within a specified project.
    Only available to admins and power users.
    ---
    tags:
      - floating ips
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: floating_ip_parameters
        in: body
        description: parameters for floating IP creation
        required: true
        schema:
            id: FloatingIPParameters
            type: object
            required:
              - project_id
            properties:
                project_id:
                    type: string
                    description: ID of project in which to create floating IP
                    default: abcd12e3f456789012345a678b9cde01
                network_id:
                    type: string
                    description: ID of external network in which to create floating IP, uses default public network if not specified
                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
    responses:
        200:
            description: Floating IP created.
            schema:
                type: object
                id: FloatingIPCreated
                required:
                    - address
                    - id
                properties:
                    address:
                        type: string
                        description: address of floating IP
                        default: 127.0.0.1
                    id:
                        type: string
                        description: ID of floating IP
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        l3 = layer_three_ops(auth)
        # admin / power user only
        if auth['user_level'] == 2:
            abort(401, 'Not authroized. Only admins and power users can create floating IPs.')
        try:
            data = request.get_data()
            json_data = json.loads(data)
        except:
            abort(400, 'Bad request. Body must be in JSON format.')
        floating_ip_create = {}
        # required
        try:
            floating_ip_create['project_id'] = json_data['project_id']
            # check project_id
            validate_project(floating_ip_create['project_id'], auth)
        except HTTPException as he:
            raise he
        except:
            abort(400, 'Bad request. Body must contain project_id.')
        # optional
        if 'network_id' in json_data:
            floating_ip_create['ext_net_id'] = json_data['network_id']
        else:
            floating_ip_create['ext_net_id'] = util.get_default_pub_net_id()
        floating_ip_info = l3.allocate_floating_ip(floating_ip_create)
        # check floating ip creation succes
        if floating_ip_info is not None:
            # normalize output
            floating_ip =   {
                                'address':          floating_ip_info['floating_ip'],
                                'id':               floating_ip_info['floating_ip_id']
                            }
            return jsonify({'floating_ip': floating_ip})
        else:
            abort(500, 'Internal error. Unable to create floating IP.')
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred creating floating IP.' %(fe))


# action
@app.route('/v1.0/floating_ips/<string:floating_ip_id>/action', methods=['POST'])
def action_floating_ip(floating_ip_id):
    """
    Performs an action with a specified floating IP by ID.
    Associate floating IP with or disassociate floating IP from an instance.
    The response key will be the action, add or remove.
    Only performs floating IP action if the requesting user has access and the action is viable.
    ---
    tags:
      - floating ips
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: floating_ip_id
        in: path
        type: string
        required: true
        description: ID of target floating IP
      - name: floating_ip_action
        in: body
        description: parameters for floating IP action
        required: true
        schema:
            id: FloatingIPAction
            type: object
            required:
              - project_id
              - instance_id
              - action
            properties:
                project_id:
                    type: string
                    description: ID of project in which floating IP resides
                    default: abcd12e3f456789012345a678b9cde01
                instance_id:
                    type: string
                    description: ID of instance with which the floating IP action will be performed
                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
                action:
                    type: string
                    description: add to associate, remove to disassociate
                    default: add
    responses:
        200:
            description: Floating IP action performed.
            schema:
                type: object
                id: FloatingIPActionSuccess
                required:
                    - address
                    - id
                    - instance_name
                    - instance_id
                properties:
                    address:
                        type: string
                        description: address of floating IP
                        default: 127.0.0.1
                    id:
                        type: string
                        description: ID of floating IP
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    instance_name:
                        type: string
                        description: name of instance with which the floating IP action was performed
                        default: Instance_1
                    instance_id:
                        type: string
                        description: ID of instance with which the floating IP action was performed
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
        400:
            description: Bad request.
        401:
            description: Not authorized.
        404:
            description: Not found.
        409:
            description: Conflict.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        l3 = layer_three_ops(auth)
        # check floating_ip_id
        floating_ip_details = validate_floating_ip(floating_ip_id, auth)
        try:
            data = request.get_data()
            json_data = json.loads(data)
        except:
            abort(400, 'Bad request. Body must be in JSON format.')
        floating_ip_action = {}
        # required
        try:
            floating_ip_action['project_id'] = json_data['project_id']
            floating_ip_action['instance_id'] = json_data['instance_id']
            # check action
            if json_data['action'] != "add" and json_data['action'] != "remove":
                abort(400, 'Bad request. Floating IP action must be add or remove.')
            floating_ip_action['action'] = json_data['action']
        except HTTPException as he:
            raise he
        except:
            abort(400, 'Bad request. Body must contain project_id, instance_id and action.')
        # make sure action is viable
        if floating_ip_action['action'] == "add" and floating_ip_details['instance_id'] == "" or floating_ip_action['action'] == "remove" and floating_ip_details['instance_id'] != "":
            floating_ip_action['floating_ip'] = floating_ip_details['floating_ip']
            floating_ip_info = l3.update_floating_ip(floating_ip_action)
            # normalize output
            floating_ip =   {
                                'address':          floating_ip_info['floating_ip'],
                                'id':               floating_ip_info['floating_ip_id'],
                                'instance_name':    floating_ip_info['instance_name'],
                                'instance_id':      floating_ip_info['instance_id']
                            }
            return jsonify({floating_ip_action['action']: floating_ip})
        else:
            abort(409, 'Conflict. Unable to perform %s using floating IP %s because the action is not viable, either associating when already associated or disassociating when already disassociated.' %(floating_ip_action['action'], floating_ip_id))
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred performing %s using floating IP %s.' %(fe, floating_ip_action['action'], floating_ip_id))


# delete
@app.route('/v1.0/floating_ips/<string:floating_ip_id>', methods=['DELETE'])
def delete_floating_ip(floating_ip_id):
    """
    Deletes a specified floating IP by ID.
    Only available to admins and power users.
    ---
    tags:
      - floating ips
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: floating_ip_id
        in: path
        type: string
        required: true
        description: ID of target floating IP
    responses:
        200:
            description: Floating IP deleted.
            schema:
                type: object
                id: ObjectDeleted
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        l3 = layer_three_ops(auth)
        # admin / power user only
        if auth['user_level'] == 2:
            abort(401, 'Not authorized. Only admins and power users can delete floating IPs.')
        # check floating_ip_id
        floating_ip_delete = validate_floating_ip(floating_ip_id, auth)
        floating_ip_info = l3.deallocate_floating_ip(floating_ip_delete)
        # check floating ip deletion success
        if floating_ip_info == "OK":
            # normalize output
            floating_ip =   {
                                'id':               floating_ip_id
                            }
            return jsonify({'floating_ip': floating_ip})
        else:
            abort(500, 'Internal error. Unable to delete floating IP %s.' %(floating_ip_id))
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred deleting floating IP %s.' %(fe, floating_ip_id))


# --- Volumes ----

# get all in cloud
@app.route('/v1.0/volumes', methods=['GET'])
def get_all_volumes():
    """
    Lists all volumes.
    Only returns volumes to which the requesting user has access.
    ---
    tags:
      - volumes
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
    responses:
        200:
            description: Volumes listed.
            schema:
                type: array
                id: Volumes
                items:
                    schema:
                        type: object
                        id: Volume
                        required:
                          - name
                          - id
                          - type
                          - project_id
                        properties:
                            name:
                                type: string
                                description: name of volume
                                default: Project_1
                            id:
                                type: string
                                description: ID of volume
                                default: 1234a56b-8901-2345-67c8-90de12f34ab5
                            type:
                                type: string
                                description: type of volume, ssd or spindle
                                default: ssd
                            project_id:
                                type: string
                                description: ID of volumes's project
                                default: abcd12e3f456789012345a678b9cde01
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        vo = volume_ops(auth)
        volumes = []
        volumes_info = vo.list_volumes()
        # normalize output
        for info in volumes_info:
            volume =    {
                            "name":         info['volume_name'],
                            "id":           info['volume_id'],
                            "type":         info['volume_type'],
                            "project_id":   info['project_id']
                        }
            volumes.append(volume)
        return jsonify({'volumes': volumes})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred listing volumes.' %(fe))


# get all in project
@app.route('/v1.0/<string:project_id>/volumes', methods=['GET'])
def get_volumes(project_id):
    """
    Lists all volumes in specified project by ID.
    Only returns volumes to which the requesting user has access.
    ---
    tags:
      - volumes
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
    responses:
        200:
            description: Volumes listed.
            schema:
                type: array
                id: Volumes
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        vo = volume_ops(auth)
        # check project_id
        validate_project(project_id, auth)
        volumes = []
        volumes_info = vo.list_volumes(project_id)
        # normalize output
        for info in volumes_info:
            volume =    {
                            "name":         info['volume_name'],
                            "id":           info['volume_id'],
                            "type":         info['volume_type'],
                            "project_id":   info['project_id']
                        }
            volumes.append(volume)
        return jsonify({'volumes': volumes})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred listing volumes in project %s.' %(fe))


# get
@app.route('/v1.0/<string:project_id>/volumes/<string:volume_id>', methods=['GET'])
def get_volume(project_id, volume_id):
    """
    Gets detailed information about a specified volume by ID.
    Only returns volume information to which the requesting user has access.
    ---
    tags:
      - volumes
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: volume_id
        in: path
        type: string
        required: true
        description: ID of target volume
    responses:
        200:
            description: Volume found.
            schema:
                type: object
                id: VolumeDetails
                required:
                    - name
                    - id
                    - type
                    - size
                    - is_attached
                    - instance_name
                    - instance_id
                    - mount_point
                properties:
                    name:
                        type: string
                        description: name of volume
                        default: Volume_1
                    id:
                        type: string
                        description: ID of volume
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    type:
                        type: string
                        description: type of volume, ssd or spindle
                        default: ssd
                    size:
                        type: integer
                        description: size of volume in GB
                        default: 10
                    is_attached:
                        type: boolean
                        description: conveying if volume is attached to an instance
                        default: false
                    instance_name:
                        type: string
                        description: name of instance to which the volume is attached
                        default: Instance_1
                    instance_id:
                        type: string
                        description: ID of instance to which the volume is attached
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    mount_point:
                        type: string
                        description: mount point of volume on instance
                        default: /vda
        400:
            description: Bad request.
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        vo = volume_ops(auth)
        # check project_id
        validate_project(project_id, auth)
        # check volume_id
        volume_info = validate_volume(volume_id, project_id, auth)
        # normalize output
        if volume_info['volume_attached'] == "true":
            volume_info['volume_attached'] = True
        else:
            volume_info['volume_attached'] = False
        volume =   {
                        'name':             volume_info['volume_name'],
                        'id':               volume_info['volume_id'],
                        'type':             volume_info['volume_type'],
                        'size':             volume_info['volume_size'],
                        'is_attached':      volume_info['volume_attached'],
                        'instance_name':    volume_info['volume_instance_name'],
                        'instance_id':      volume_info['volume_instance'],
                        'mount_point':      volume_info['volume_mount_location']
                    }
        return jsonify({'volume': volume})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred getting details for volume %s.' %(fe, volume_id))

# TODO

# create
@app.route('/v1.0/<string:project_id>/volumes', methods=['POST'])
def create_volume(project_id):
    """
    Creates a volume within a specified project.
    May only specify image_id, snapshot_id or volume_id, not any combination of these parameters.
    If image_id is specified, the volume will be created as a bootable volume.
    ---
    tags:
      - volumes
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: volume_parameters
        in: body
        description: parameters for volume creation
        required: true
        schema:
            id: VolumeParameters
            type: object
            required:
              - name
              - size
            properties:
                name:
                    type: string
                    description: name for volume
                    default: Volume_1
                size:
                    type: integer
                    description: size for volume in GB
                    default: 10
                type:
                    type: string
                    description: type for volume, ssd or spindle, uses ssd if not specified
                    default: ssd
                snapshot_id:
                    type: string
                    description: ID of volume snapshot from which to create volume if creating volume from snapshot
                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
                volume_id:
                    type: string
                    description: ID of volume from which to clone volume if cloning volume
                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
                zone:
                    type: string
                    description: availability zone for volume, uses nova if not specified
                    default: nova
                image_id:
                    type: string
                    description: ID of image to use when creating bootable volume
                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
    responses:
        200:
            description: Volume created.
            schema:
                type: object
                id: VolumeCreated
                required:
                    - name
                    - id
                    - type
                    - size
                properties:
                    name:
                        type: string
                        description: name of volume
                        default: Volume_1
                    id:
                        type: string
                        description: ID of volume
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    type:
                        type: string
                        description: type of volume, ssd or spindle
                        default: ssd
                    size:
                        type: integer
                        description: size of volume in GB
                        default: 10
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        vo = volume_ops(auth)
        try:
            data = request.get_data()
            json_data = json.loads(data)
        except:
            abort(400, 'Bad request. Body must be in JSON format.')
        volume_create = {}
        # check project_id
        validate_project(project_id, auth)
        volume_create['project_id'] = project_id
        # required
        try:
            volume_create['volume_name'] = json_data['name']
            volume_create['volume_size'] = json_data['size']
        except:
            abort(400, 'Bad request. Body must contain name and size.')
        # optional
        if 'type' in json_data:
            volume_create['volume_type'] = json_data['type']
        if 'snapshot_id' in json_data:
            # check volume snapshot_id
            validate_volume_snapshot(json_data['snapshot_id'], auth)
            volume_create['snapshot_id'] = json_data['snapshot_id']
        if 'volume_id' in json_data:
            # check volume_id
            validate_volume(json_data['volume_id'], project_id, auth)
            volume_create['source_vol_id'] = json_data['volume_id']
        if 'zone' in json_data:
            volume_create['volume_zone'] = json_data['zone']
        if 'image_id' in json_data:
            validate_image(json_data['image_id'], auth)
            volume_create['image_id'] = json_data['image_id']
            volume_create['volume_bootable'] = "true"
        # check optional paramters
        if 'image_id' in volume_create and 'snapshot_id' in volume_create or 'snapshot_id' in volume_create and 'volume_id' in volume_create or 'volume_id' in volume_create and 'image_id' in volume_create:
            abort(400, 'Bad request. May only specify image_id, snapshot_id or volume_id, not any combination of these parameters.')
        try:
            volume_info = vo.create_volume(volume_create)
            # normalize output
            volume =    {
                            'name': volume_info['volume_name'],
                            'id':   volume_info['volume_id'],
                            'type': volume_info['volume_type'],
                            'size': volume_info['volume_size']
                        }
            return jsonify({'volume': volume})
        except Exception as e:
            abort(500, 'Internal error. Error <%s> occurred creating volume.' %(e))
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred creating volume.' %(fe))


# action
@app.route('/v1.0/<string:project_id>/volumes/<string:volume_id>/action', methods=['POST'])
def action_volume(project_id, volume_id):
    """
    Performs an action with a specified volume by ID.
    Attach volume to or detach volume from an instance.
    Only performs volume action if the requesting user has access.
    ---
    tags:
      - volumes
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: volume_id
        in: path
        type: string
        required: true
        description: ID of target volume
      - name: volume_action
        in: body
        description: parameters for volume action
        required: true
        schema:
            id: VolumeAction
            type: object
            required:
              - instance_id
              - action
            properties:
                instance_id:
                    type: string
                    description: ID of instance with which the volume action will be performed
                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
                action:
                    type: string
                    description: add to attach, remove to detach
                    default: add
    responses:
        200:
            description: Volume action performed.
            schema:
                type: object
                id: VolumeActionSuccess
                required:
                    - name
                    - id
                    - instance_name
                    - instance_id
                properties:
                    name:
                        type: string
                        description: name of volume
                        default: Volume_1
                    id:
                        type: string
                        description: ID of volume
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    instance_name:
                        type: string
                        description: name of instance with which the volume action was performed
                        default: Instance_1
                    instance_id:
                        type: string
                        description: ID of instance with which the volume action was performed
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
        400:
            description: Bad request.
        401:
            description: Not authorized.
        404:
            description: Not found.
        409:
            description: Conflict.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        sso = server_storage_ops(auth)
        try:
            data = request.get_data()
            json_data = json.loads(data)
        except:
            abort(400, 'Bad request. Body must be in JSON format.')
        volume_action = {}
        # check project_id
        validate_project(project_id, auth)
        volume_action['project_id'] = project_id
        # check volume_id
        volume_details = validate_volume(volume_id, project_id, auth)
        volume_action['volume_id'] = volume_id
        # required
        try:
            # check instance_id
            instance_info = validate_instance(json_data['instance_id'], project_id, auth)
            volume_action['instance_id'] = json_data['instance_id']
            volume_action['mount_point'] = "/dev/vdc"
            # check action
            if json_data['action'] != "add" and json_data['action'] != "remove":
                abort(400, 'Bad request. Volume action must be add or remove.')
            volume_action['action'] = json_data['action']
        except HTTPException as he:
            raise e
        except:
            abort(400, 'Bad request. Body must contain instance_id and action.')
        # check resources in same project
        if instance_info['project_id'] != project_id:
            abort(400, 'Bad request. Volume and instance must reside in the same project.')
        # check action is viable
        if volume_action['action'] == "add" and volume_details['volume_attached'] == "false":
            volume_info = sso.attach_vol_to_server(volume_action)
        elif volume_action['action'] == "remove" and volume_details['volume_attached'] == "true":
            volume_info = sso.detach_vol_from_server(volume_action)
        else:
            abort(409, 'Conflict. Unable to perform %s using volume %s and instance %s because is_attached = %s.' %(volume_action['action'], volume_id, volume_action['instance_id'], volume_details['volume_attached']))
        # check action success
        if volume_info == "OK":
            # normalize output
            volume =    {
                            'name':             volume_details['volume_name'],
                            'id':               volume_id,
                            'instance_name':    instance_info['server_name'],
                            'instance_id':      instance_info['server_id']
                        }
            return jsonify({volume_action['action']: volume})
        else:
            abort(500, 'Internal error. Unable to perform %s using volume %s and instance %s.' %(volume_action['action'], volume_id, volume_action['instance_id']))
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred performing %s using volume %s and instance %s.' %(fe, volume_action['action'], volume_id, volume_action['instance_id']))


# delete
@app.route('/v1.0/<string:project_id>/volumes/<string:volume_id>', methods=['DELETE'])
def delete_volume(project_id, volume_id):
    """
    Deletes a specified volume by ID.
    Only deletes volume if requesting user has access.
    ---
    tags:
      - volumes
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: volume_id
        in: path
        type: string
        required: true
        description: ID of target volume
    responses:
        200:
            description: Volume deleted.
            schema:
                id: ObjectDeleted
                type: object
        400:
            description: Bad request.
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        vo = volume_ops(auth)
        volume_delete = {}
        # check project_id
        validate_project(project_id, auth)
        volume_delete['project_id'] = project_id
        # check volume_id
        validate_volume(volume_id, project_id, auth)
        volume_delete['volume_id'] = volume_id
        volume_info = vo.delete_volume(volume_delete)
        # check action success
        if volume_info == "OK":
            # normalize output
            volume =    {
                            'id':   volume_id
                        }
            return jsonify({'volume': volume})
        else:
            abort(500, 'Internal error. Unable to delete volume %s.' %(volume_id))
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred deleting volume %s.' %(fe, volume_id))


# --- Networks ----

# get all
# NOTE: removed project_id from external networks
@app.route('/v1.0/networks', methods=['GET'])
def get_networks():
    """
    Lists all networks.
    Only returns networks to which the requesting user has access.
    ---
    tags:
      - networks
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
    responses:
        200:
            description: Networks listed.
            schema:
                type: object
                id: Networks
                required:
                  - internal
                  - external
                properties:
                    internal:
                        type: array
                        id: InternalNetworks
                        items:
                            schema:
                                type: object
                                id: InternalNetwork
                                required:
                                  - name
                                  - id
                                  - project_id
                                properties:
                                    name:
                                        type: string
                                        description: name of network
                                        default: Project_1
                                    id:
                                        type: string
                                        description: ID of network
                                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                                    project_id:
                                        type: string
                                        description: ID of networks's project
                                        default: abcd12e3f456789012345a678b9cde01
                                    is_in_use:
                                        type: boolean
                                        description: conveying if network is in use
                                        default: false
                                    router_id:
                                        type: string
                                        description: ID of router attached to network
                                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    external:
                        type: array
                        id: ExternalNetworks
                        items:
                            schema:
                                type: object
                                id: ExternalNetwork
                                required:
                                  - name
                                  - id
                                  - project_id
                                properties:
                                    name:
                                        type: string
                                        description: name of network
                                        default: Network_1
                                    id:
                                        type: string
                                        description: ID of network
                                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        nno = neutron_net_ops(auth)
        internal = []
        external = []
        networks =  {
                        'internal': internal,
                        'external': external
                    }
        internal_info = nno.list_internal_networks()
        # normalize output
        for info in internal_info:
            if info['router_id'] == "":
                info['router_id'] = None
            if info['in_use'] == "true":
                info['in_use'] = True
            else:
                info['in_use'] = False
            internal_network =  {
                                    'name':         info['net_name'],
                                    'id':           info['net_id'],
                                    'project_id':   info['project_id'],
                                    'is_in_use':    info['in_use'],
                                    'router_id':    info['router_id']
                                }
            internal.append(internal_network)
        external_info = nno.list_external_networks()
        for info in external_info:
            external_network =  {
                                    'name':         info['net_name'],
                                    'id':           info['net_id']
                                }
            external.append(external_network)
        return jsonify({'networks': networks})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred listing networks.' %(fe))


# get
@app.route('/v1.0/networks/<string:network_id>', methods=['GET'])
def get_network(network_id):
    """
    Gets detailed information about a specified network by ID.
    Only returns network information to which the requesting user has access.
    ---
    tags:
      - networks
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: network_id
        in: path
        type: string
        required: true
        description: ID of target network
    responses:
        200:
            description: Network found.
            schema:
                type: object
                id: NetworkDetails
                required:
                  - name
                  - id
                  - user_id
                  - is_up
                  - is_shared
                  - type
                  - subnets
                  - project_id
                  - router_id
                properties:
                    name:
                        type: string
                        description: name of network
                        default: Project_1
                    id:
                        type: string
                        description: ID of network
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    user_id:
                        type: string
                        description: ID of network's creator
                        default: abcd12e3f456789012345a678b9cde01
                    is_up:
                        type: boolean
                        description: conveying if administrative state of the network is up (true) or down (false)
                        default: true
                    is_shared:
                        type: boolean
                        description: conveying if the network is shared across projects
                        default: false
                    type:
                        type: string
                        description: type of network, internal or external
                        default: internal
                    subnets:
                        type: array
                        description: subnets of network
                        items:
                            schema:
                                type: object
                                id: SubnetInfo
                                required:
                                  - name
                                  - id
                                properties:
                                    name:
                                        type: string
                                        description: name of subnet
                                        default: Subnet_1
                                    id:
                                        type: string
                                        description: ID of subnet
                                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    project_id:
                        type: string
                        description: ID of networks's project
                        default: abcd12e3f456789012345a678b9cde01
                    router_id:
                        type: string
                        description: ID of networks's router
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        # check network_id
        network_info = validate_network(network_id, auth)
        # normalize output
        if network_info['net_admin_state'] == "true":
            network_info['net_admin_state'] = True
        else:
            network_info['net_admin_state'] = False
        if network_info['net_shared'] == "true":
            network_info['net_shared'] = True
        else:
            network_info['net_shared'] = False
        if network_info['net_internal'] == "true":
            network_info['net_internal'] = "internal"
        else:
            network_info['net_internal'] = "external"
            # NOTE: removing project_id from external networks
            network_info['project_id'] = None
        subnets = []
        for info in network_info['net_subnet_id']:
            subnet =    {
                            'name': info['subnet_name'],
                            'id':   info['subnet_id']
                        }
            subnets.append(subnet)
        network =   {
                        'name':         network_info['net_name'],
                        'id':           network_info['net_id'],
                        'user_id':      network_info['net_creator_id'],
                        'is_up':        network_info['net_admin_state'],
                        'is_shared':    network_info['net_shared'],
                        'type':         network_info['net_internal'],
                        'subnets':      subnets,
                        'project_id':   network_info['project_id'],
                        'router_id':    network_info['router_id']
                    }
        return jsonify({'network': network})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred getting details for network %s.' %(fe, network_id))


# --- Routers ----

# get all
@app.route('/v1.0/routers', methods=['GET'])
def get_routers():
    """
    Lists all routers.
    Only returns routers to which the requesting user has access.
    ---
    tags:
      - routers
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
    responses:
        200:
            description: Routers listed.
            schema:
                type: array
                id: Routers
                items:
                    schema:
                        type: object
                        id: Router
                        required:
                          - name
                          - id
                          - status
                        properties:
                            name:
                                type: string
                                description: name of router
                                default: Router_1
                            id:
                                type: string
                                description: ID of router
                                default: 1234a56b-8901-2345-67c8-90de12f34ab5
                            status:
                                type: string
                                description: status of router
                                default: ACTIVE
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        l3 = layer_three_ops(auth)
        routers = []
        router_info = l3.list_routers()
        # normalize output
        for info in router_info:
            router =    {
                            'name':     info['router_name'],
                            'id':       info['router_id'],
                            'status':   info['router_status']
                        }
            routers.append(router)
        return jsonify({'routers': routers})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred listing routers.' %(fe))


# get
@app.route('/v1.0/routers/<string:router_id>', methods=['GET'])
def get_router(router_id):
    """
    Gets detailed information about a specified router by ID.
    Only returns router information to which the requesting user has access.
    ---
    tags:
      - routers
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: router_id
        in: path
        type: string
        required: true
        description: ID of target router
    responses:
        200:
            description: Router found.
            schema:
                type: object
                id: RouterDetails
                required:
                  - name
                  - id
                  - status
                  - project_id
                  - network_id
                  - internal_subnet_id
                  - internal_port_id
                  - external_gateway_id
                  - external_address
                  - is_up
                properties:
                    name:
                        type: string
                        description: name of router
                        default: Project_1
                    id:
                        type: string
                        description: ID of router
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    status:
                        type: string
                        description: status of router
                        default: ACTIVE
                    project_id:
                        type: string
                        description: ID of routers's project
                        default: abcd12e3f456789012345a678b9cde01
                    network_id:
                        type: string
                        description: ID of router's network
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    internal_subnet_id:
                        type: string
                        description: ID of router's internal subnet
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    internal_port_id:
                        type: string
                        description: ID of router's internal port
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    external_gateway_id:
                        type: string
                        description: ID of routers's external gateway
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    external_address:
                        type: string
                        description: external IP address of router
                        default: 127.0.0.1
                    is_up:
                        type: boolean
                        description: conveying if administrative state of the network is up (true) or down (false)
                        default: true
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        # check router_id
        router_info = validate_router(router_id, auth)
        # normalize output
        if router_info['admin_state_up'] == "true":
            router_info['admin_state_up'] = True
        else:
            router_info['admin_state_up'] = False
        router =   {
                        'name':                 router_info['router_name'],
                        'id':                   router_info['router_id'],
                        'status':               router_info['router_status'],
                        'project_id':           router_info['project_id'],
                        'network_id':           router_info['network_id'],
                        'internal_subnet_id':   router_info['router_int_sub_id'],
                        'internal_port_id':     router_info['internal_port'],
                        'external_gateway_id':  router_info['external_gateway'],
                        'external_address':     router_info['external_ip'],
                        'is_up':                router_info['admin_state_up']
                    }
        return jsonify({'router': router})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred getting details for router %s.' %(fe, router_id))


# --- Users ----
# this will need revision once we clean up the back-end,
# will move to /vX.Y/users for everything

# get all in cloud
@app.route('/v1.0/users', methods=['GET'])
def get_all_users():
    """
    Lists all users.
    Only returns users to which the requesting user has access.
    ---
    tags:
      - users
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
    responses:
        200:
            description: Users listed.
            schema:
                type: array
                id: Users
                items:
                    schema:
                        type: object
                        id: User
                        required:
                          - name
                          - id
                        properties:
                            name:
                                type: string
                                description: name of user
                                default: User_1
                            id:
                                type: string
                                description: ID of user
                                default: abcd12e3f456789012345a678b9cde01
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        uo = user_ops(auth)
        to = tenant_ops(auth)
        users = []
        # admins can list all users
        if auth['user_level'] != 2:
            user_info = uo.list_cloud_users()
        # otherwise list all user has access to
        else:
            user_info = to.list_tenant_users(auth['project_id'])
        # normalize output
        for info in user_info:
            if 'keystone_user_id' in info:
                info['user_id'] = info['keystone_user_id']
            user =    {
                            'name':         info['username'],
                            'id':           info['user_id']
                        }
            users.append(user)
        # remove admin and shadow_admin
        users[:] = [u for u in users if u.get('name') != "admin" and u.get('name') != "shadow_admin"]
        return jsonify({'users': users})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred listing all users.' %(fe))


# get all in project
@app.route('/v1.0/<string:project_id>/users', methods=['GET'])
def get_users(project_id):
    """
    Lists all users in a specified project by ID.
    Only returns users to which the requesting user has access.
    ---
    tags:
      - users
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
    responses:
        200:
            description: Users listed.
            schema:
                id: Users
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        to = tenant_ops(auth)
        # check project_id
        validate_project(project_id, auth)
        users = []
        user_info = to.list_tenant_users(project_id)
        # normalize output
        for info in user_info:
            user =    {
                            'name':         info['username'],
                            'id':           info['user_id']
                        }
            users.append(user)
        return jsonify({'users': users})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred listing users in project %s.' %(fe, project_id))


# get
@app.route('/v1.0/<string:project_id>/users/<string:user_id>', methods=['GET'])
def get_user(project_id, user_id):
    """
    Gets detailed information about a specified user by ID.
    Only returns user information to which the requesting user has access.
    ---
    tags:
      - users
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: user_id
        in: path
        type: string
        required: true
        description: ID of target user
    responses:
        200:
            description: User found.
            schema:
                type: object
                id: UserDetails
                required:
                    - name
                    - id
                    - project_name
                    - project_id
                    - role
                    - email
                    - is_enabled
                properties:
                    name:
                        type: string
                        description: name of user
                        default: User_1
                    id:
                        type: string
                        description: ID of user
                        default: abcd12e3f456789012345a678b9cde01
                    project_name:
                        type: string
                        description: name of user's project
                        default: Project_1
                    project_id:
                        type: string
                        description: ID of user's project
                        default: abcd12e3f456789012345a678b9cde01
                    role:
                        type: string
                        description: role of user in cloud, admin, power user or user
                        default: user
                    email:
                        type: string
                        description: email of user
                        default: user_1@email.com
                    is_enabled:
                        type: boolean
                        description: conveying if user is enabled
                        default: true
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        # check project_id
        validate_project(project_id, auth)
        # check user_id
        user_info = validate_user(user_id, project_id, auth)
        # normalize output
        if user_info['user_enabled'] == "TRUE":
            user_info['user_enabled'] = True
        else:
            user_info['user_enabled'] = False
        user =    {
                        'name':         user_info['username'],
                        'id':           user_info['user_id'],
                        'project_name': user_info['project_name'],
                        'project_id':   user_info['project_id'],
                        'role':         user_info['user_role'],
                        'email':        user_info['email'],
                        'is_enabled':   user_info['user_enabled']
                    }
        return jsonify({'user': user})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred getting details for user %s.' %(fe, user_id))


# create
@app.route('/v1.0/<string:project_id>/users', methods=['POST'])
def create_user(project_id):
    """
    Creates a specified user.
    Only available to admins.
    ---
    tags:
      - users
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: user_parameters
        in: body
        description: parameters for user creation
        required: true
        schema:
            id: UserParameters
            type: object
            required:
              - name
              - password
              - role
              - email
            properties:
                name:
                    type: string
                    description: name for user
                    default: User_1
                password:
                    type: string
                    description: password for user
                    default: password
                role:
                    type: string
                    description: role for user, admin (admin), pu (power user) or user (user)
                    default: user
                email:
                    type: string
                    description: email for user
                    default: user_1@email.com
    responses:
        200:
            description: User created.
            schema:
                id: UserCreated
                type: object
                required:
                  - name
                  - id
                  - project_id
                properties:
                    name:
                        type: string
                        description: name of user
                        default: Project_1
                    id:
                        type: string
                        description: ID of user
                        default: abcd12e3f456789012345a678b9cde01
                    project_id:
                        type: string
                        description: ID of user's project_id
                        default: abcd12e3f456789012345a678b9cde01
        400:
            description: Bad request.
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        # check is_admin
        if auth['is_admin'] != 1:
            abort(401, 'Not authroized. Only admins can create users.')
        uo = user_ops(auth)
        try:
            data = request.get_data()
            json_data = json.loads(data)
        except:
            abort(400, 'Bad request. Body must be in JSON format.')
        user_create = {}
        # check project_id
        validate_project(project_id, auth)
        user_create['project_id'] = project_id
        # required
        try:
            user_create['username'] = json_data['name']
            user_create['password'] = json_data['password']
            # check role
            if json_data['role'] != "admin" and json_data['role'] != "pu" and json_data['role'] != "user":
                abort(400, 'Bad request. User role must be admin, pu or user.')
            user_create['user_role'] = json_data['role']
            user_create['email'] = json_data['email']
        except HTTPException as he:
            raise e
        except:
            abort(400, 'Bad request. Body must contain name, password, role and email.')
        user_info = uo.create_user(user_create)
        # normalize output
        user =  {
                    'name':         user_info['username'],
                    'id':           user_info['user_id'],
                    'project_id':   user_info['project_id']
                }
        return jsonify({'user': user})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred creating user.' %(fe))


# action
@app.route('/v1.0/<string:project_id>/users/<string:user_id>/action', methods=['POST'])
def action_user(project_id, user_id):
    """
    Performs an action with a specified user by ID.
    Add existing user to or remove user from a project.
    To add a user, the user must exist and not be in a project.
    To remove a user, the user must exists and be in a project.
    Only available to admins.
    ---
    tags:
      - users
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project_id
      - name: user_id
        in: path
        type: string
        required: true
        description: ID of target user_id
      - name: user_action
        in: body
        description: parameters for user action
        required: true
        schema:
            id: UserAction
            type: object
            required:
              - action
            properties:
                role:
                    type: string
                    description: role for user when adding to a project (this can be different from user's original role), admin (admin), pu (power user) or user (user), required when adding a user to a project
                    default: user
                is_primary:
                    type: boolean
                    description: conveying if the user's primary project should be updated when adding to a project (this should only be true when adding an admin to a project and this is explicitly desired), uses false is not specified
                    default: false
                action:
                    type: string
                    description: user action, add or remove
                    default: add
    responses:
        200:
            description: User action performed.
            schema:
                type: object
                id: UserActionSuccess
                required:
                    - name
                    - id
                    - project_name
                    - project_id
                properties:
                    name:
                        type: string
                        description: name of user
                        default: User_1
                    id:
                        type: string
                        description: ID of user
                        default: abcd12e3f456789012345a678b9cde01
                    project_name:
                        type: string
                        description: name of project with which the user action was performed
                        default: Project_1
                    project_id:
                        type: string
                        description: ID of project with which the user action was performed
                        default: abcd12e3f456789012345a678b9cde01
        400:
            description: Bad request.
        401:
            description: Not authorized.
        404:
            description: Not found.
        409:
            description: Conflict.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        # check is_admin
        if auth['is_admin'] != 1:
            abort(401, 'Not authroized. Only admins can perform user actions.')
        uo = user_ops(auth)
        try:
            data = request.get_data()
            json_data = json.loads(data)
        except:
            abort(400, 'Bad request. Body must be in JSON format.')
        user_action = {}
        # check project_id
        project_info = validate_project(project_id, auth)
        user_action['project_id'] = project_id
        # required
        try:
            # check action
            if json_data['action'] != "add" and json_data['action'] != "remove":
                abort(400, 'Bad request. user action must be add or remove.')
            user_action['action'] = json_data['action']
            # check user_id
            if user_action['action'] == "remove":
                user_details = validate_user(user_id, project_id, auth)
                user_action['user_id'] = user_id
                user_action['username'] = user_details['username']
        except HTTPException as he:
            raise e
        except:
            abort(400, 'Bad request. Body must contain action.')
        # get orphans to verify user action
        orphans = uo.list_orphaned_users()
        is_orphan = False
        for orphan in orphans:
            if user_id == orphan['keystone_user_id']:
                is_orphan = True
                user_action['username'] = orphan['username']
                break
        # optional
        if 'role' in json_data:
            # check role
            if json_data['role'] != "admin" and json_data['role'] != "pu" and json_data['role'] != "user":
                abort(400, 'Bad request. User role must be admin, pu or user.')
            user_action['user_role'] = json_data['role']
        if 'is_primary' in json_data:
            user_action['update_primary'] = json_data['is_primary']
        # check action is viable
        if user_action['action'] == "add" and 'user_role' in user_action and is_orphan is True:
            user_info = uo.add_user_to_project(user_action)
        elif user_action['action'] == "remove" and is_orphan is False:
            user_info = uo.remove_user_from_project(user_action)
        else:
            abort(409, 'Conflict. Unable to perform %s using user %s and project %s because user is ineligible or not enough parameters were specified for the action.' %(json_data['action'], user_id, project_id))
        # check user action success
        if user_action['action'] == "add" or user_action['action'] == "remove" and user_info == "OK":
            # normalize output
            user =  {
                        'name':         user_action['username'],
                        'id':           user_id,
                        'project_name': project_info['project_name'],
                        'project_id':   project_info['project_id']
                    }
            return jsonify({str(user_action['action']): user})
        else:
            abort(500, 'Internal error. Unable to perform %s using user %s and project %s.' %(user_action['action'], user_id, project_id))
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred performing %s using user %s and project %s.' %(fe, user_action['action'], user_id, project_id))


# delete
@app.route('/v1.0/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Deletes a specified user by ID.
    Only available to admins.
    ---
    tags:
      - users
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: user_id
        in: path
        type: string
        required: true
        description: ID of target user
    responses:
        200:
            description: User deleted.
            schema:
                id: ObjectDeleted
                type: object
        400:
            description: Bad request.
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        # check is_admin
        if auth['is_admin'] != 1:
            abort(401, 'Not authroized. Only admins can perform user actions.')
        uo = user_ops(auth)
        user_delete = {}
        user_delete['user_id'] = user_id
        # check user_id
        users = uo.list_cloud_users()
        for user in users:
            if user_id == user['keystone_user_id']:
                user_delete['username'] = user['username']
                break
        if 'username' not in user_delete:
            abort(404, 'Not found. Could not find user %s.' %(user_id))
        user_info = uo.delete_user(user_delete)
        # check user delete success
        if user_info == "OK":
            # normalize output
            user =  {
                        'id':   user_id
                    }
            return jsonify({'user': user})
        else:
            abort(500, 'Internal error. Unable to delete user %s.' %(user_id))
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred deleting user %s.' %(fe, user_id))


# --- Security Groups ----

# get all in cloud
@app.route('/v1.0/security_groups', methods=['GET'])
def get_all_security_groups():
    """
    Lists all security groups.
    Only returns security groups to which the requesting user has access.
    ---
    tags:
      - security groups
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
    responses:
        200:
            description: Security groups listed.
            schema:
                type: array
                id: SecurityGroups
                items:
                    schema:
                        type: object
                        id: SecurityGroup
                        required:
                          - name
                          - id
                        properties:
                            name:
                                type: string
                                description: name of security group
                                default: Security_Group_1
                            id:
                                type: string
                                description: ID of security group
                                default: 1234a56b-8901-2345-67c8-90de12f34ab5
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        so = server_ops(auth)
        to = tenant_ops(auth)
        security_groups = []
        # admins can list all security groups
        if auth['is_admin'] == 1:
            security_group_info = []
            projects = to.list_all_tenants()
            for project in projects:
                security_group_info.extend(so.list_sec_group(project['project_id']))
        # otherwise list all user has acces to
        else:
            security_group_info = so.list_sec_group(auth['project_id'])
        # normalize output
        for info in security_group_info:
            security_group =    {
                                    'name': info['sec_group_name'],
                                    'id':   info['sec_group_id']
                                }
            security_groups.append(security_group)
        return jsonify({'security_groups': security_groups})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred listing security groups.' %(fe))


# get all in project
@app.route('/v1.0/<string:project_id>/security_groups', methods=['GET'])
def get_security_groups(project_id):
    """
    Lists all security groups in a project specified by ID.
    Only returns security groups to which the requesting user has access.
    ---
    tags:
      - security groups
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
    responses:
        200:
            description: Security groups listed.
            schema:
                type: array
                id: SecurityGroups
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        so = server_ops(auth)
        # check project_id
        validate_project(project_id, auth)
        security_groups = []
        security_group_info = so.list_sec_group(project_id)
        # normalize output
        for info in security_group_info:
            security_group =    {
                                    'name': info['sec_group_name'],
                                    'id':   info['sec_group_id']
                                }
            security_groups.append(security_group)
        return jsonify({'security_groups': security_groups})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred listing security groups in project %s.' %(fe, project_id))


# get
@app.route('/v1.0/<string:project_id>/security_groups/<string:security_group_id>', methods=['GET'])
def get_security_group(project_id, security_group_id):
    """
    Gets detailed information about a specified security group by ID.
    Only returns security group information to which the requesting user has access.
    ---
    tags:
      - security groups
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: security_group_id
        in: path
        type: string
        required: true
        description: ID of target security group
    responses:
        200:
            description: Security groups listed.
            schema:
                type: object
                id: SecurityGroupDetails
                required:
                  - name
                  - id
                  - rules
                properties:
                    name:
                        type: string
                        description: name of security group
                        default: Security_Group_1
                    id:
                        type: string
                        description: ID of security group
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    rules:
                        type: object
                        description: security group rules
                        schema:
                            type: object
                            id: Rules
                            required:
                              - tcp
                              - udp
                            properties:
                                tcp:
                                    type: array
                                    id: TCPRules
                                    items:
                                        schema:
                                            type: object
                                            id: Rule
                                            required:
                                              - id
                                              - start
                                              - end
                                              - cidr
                                            properties:
                                                id:
                                                    type: string
                                                    description: ID of security group rule
                                                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
                                                start:
                                                    type: integer
                                                    description: first port in security group rule
                                                    default: 22
                                                end:
                                                    type: integer
                                                    description: last port in security group rule
                                                    default: 22
                                                cidr:
                                                    type: string
                                                    description: cidr address representation of security group rule
                                                    default: 127.0.0.1/18
                                udp:
                                    type: array
                                    id: UDPRules
                                    items:
                                        schema:
                                            type: object
                                            id: Rule
                                            required:
                                              - id
                                              - start
                                              - end
                                              - cidr
                                            properties:
                                                id:
                                                    type: string
                                                    description: ID of security group rule
                                                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
                                                start:
                                                    type: integer
                                                    description: first port in security group rule
                                                    default: 22
                                                end:
                                                    type: integer
                                                    description: last port in security group rule
                                                    default: 22
                                                cidr:
                                                    type: string
                                                    description: cidr address representation of security group rule
                                                    default: 127.0.0.1/18
        400:
            description: Bad request.
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        # check project_id
        validate_project(project_id, auth)
        # check security_group_id
        security_group_info = validate_security_group(security_group_id, project_id, auth)
        # normalize output
        tcp = []
        udp = []
        rules = {}
        for port in security_group_info['ports']:
            for key in port:
                if port[key] == "None":
                    port[key] = None
            if port['transport'] == 'tcp':
                tcp_port =  {
                                'id':       port['rule_id'],
                                'start':    int(port['from_port']),
                                'end':      int(port['to_port']),
                                'cidr':     port['cidr']
                            }
                tcp.append(tcp_port)
            if port['transport'] == 'udp':
                udp_port =  {
                                'id':       port['rule_id'],
                                'start':    int(port['from_port']),
                                'end':      int(port['to_port']),
                                'cidr':     port['cidr']
                            }
                udp.append(udp_port)
        rules['tcp'] = tcp
        rules['udp'] = udp
        security_group =    {
                                'name':     security_group_info['sec_group_name'],
                                'id':       security_group_info['sec_group_id'],
                                'rules':    rules
                            }
        return jsonify({'security_group': security_group})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred getting details for security group %s.' %(fe, security_group_id))


# create
@app.route('/v1.0/<string:project_id>/security_groups', methods=['POST'])
def create_security_group(project_id):
    """
    Creates a security group within a specified project.
    May only create a security group with one type of transport.  Other transports can be added later.
    Only creates security group if the requesting user has access.
    ---
    tags:
      - security groups
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: security_group_parameters
        in: body
        description: parameters for security group creation
        required: true
        schema:
            id: SecurityGroupParameters
            type: object
            required:
              - name
            properties:
                name:
                    type: string
                    description: name for security group
                    default: Security_Group_1
                type:
                    type: string
                    description: transport type for security group rules, tcp or udp, uses tcp if not specified
                    default: tcp
                ports:
                    type: array
                    description: allowed ports for security group, uses ['22', '80', '443', '3389'] if not specified, rules in the form of <mix>-<max> are allowed (ex = ['22', '80', '443', '1100-1200', '3389'])
                    default: ['22', '80', '443', '3389']
                    items:
                        type: string
                        description: allowed port for security group
    responses:
        200:
            description: Security group created.
            schema:
                type: object
                id: SecurityGroupCreated
                required:
                    - name
                    - id
                properties:
                    name:
                        type: string
                        description: name of security_group
                        default: Security_Group_1
                    id:
                        type: string
                        description: ID of security_group
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        so = server_ops(auth)
        try:
            data = request.get_data()
            json_data = json.loads(data)
        except:
            abort(400, 'Bad request. Body must be in JSON format.')
        security_group_create = {}
        # check project_id
        validate_project(project_id, auth)
        security_group_create['project_id'] = project_id
        # required
        try:
            security_group_create['group_name'] = json_data['name']
        except:
            abort(400, 'Bad request. Body must contain name.')
        # optional
        if 'type' in json_data:
            security_group_create['transport'] = json_data['type']
        if 'ports' in json_data:
            # check ports format
            validate_ports(json_data['ports'])
            security_group_create['ports'] = json_data['ports']
        security_group_info = so.create_sec_group(security_group_create)
        # normalize output
        security_group =    {
                                'name': security_group_info['sec_group_name'],
                                'id':   security_group_info['sec_group_id']
                            }
        return jsonify({'security_group': security_group})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred creating security group.' %(e))


# update
@app.route('/v1.0/<string:project_id>/security_groups/<string:security_group_id>', methods=['PUT'])
def update_security_group(project_id, security_group_id):
    """
    Updates a security group specified by ID.
    Update existing transport rules or add new ones.
    To modify existing transport rules, specify the same transport type and the updated full set of ports.
    Note that you must specify the full set of ports when modifying existing transport rules, you cannot add a single port rule while maintaining existing ones.
    To add rules for other transports, specify the other transport type and the set of ports.
    Only updates security group if the requesting user has access.
    ---
    tags:
      - security groups
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: security_group_id
        in: path
        type: string
        required: true
        description: ID of target security group.
      - name: security_group_update
        in: body
        description: parameters for security group updating
        required: true
        schema:
            id: SecurityGroupUpdate
            type: object
            properties:
                type:
                    type: string
                    description: transport type for security group rules, tcp or udp, uses tcp if not specified
                    default: tcp
                ports:
                    type: array
                    description: allowed ports for security group, uses ['22', '80', '443', '3389'] if not specified, rules in the form of <mix>-<max> are allowed (ex = ['22', '80', '443', '1100-1200', '3389'])
                    default: ['22', '80', '443', '3389']
                    items:
                        type: string
                        description: allowed port for security group
    responses:
        200:
            description: Security group created.
            schema:
                type: object
                id: SecurityGroupUpdated
                required:
                    - name
                    - id
                properties:
                    name:
                        type: string
                        description: name of security_group
                        default: Security_Group_1
                    id:
                        type: string
                        description: ID of security_group
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        so = server_ops(auth)
        try:
            data = request.get_data()
            json_data = json.loads(data)
        except:
            abort(400, 'Bad request. Body must be in JSON format.')
        security_group_update = {}
        # required            
        # check project_id
        validate_project(project_id, auth)
        security_group_update['project_id'] = project_id
        # check security_group_id
        security_group_details = validate_security_group(security_group_id, project_id, auth)
        security_group_update['group_id'] = security_group_id
        # optional
        if 'type' in json_data:
            security_group_update['transport'] = json_data['type']
        if 'ports' in json_data:
            # check ports format
            validate_ports(json_data['ports'])
            security_group_update['ports'] = json_data['ports']
        security_group_info = so.update_sec_group(security_group_update)
        # check update success
        if security_group_info == "OK":
            security_group =    {
                                    'name': security_group_details['sec_group_name'],
                                    'id':   security_group_details['sec_group_id']
                                }
            return jsonify({'security_group': security_group})
        else:
            abort(500, 'Internal error. Unable to update security group %s.' %(security_group_id))
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred updating security group %s.' %(fe, security_group_id))


# delete
@app.route('/v1.0/<string:project_id>/security_groups/<string:security_group_id>', methods=['DELETE'])
def delete_security_group(project_id, security_group_id):
    """
    Deletes a security group specified by ID.
    Only deletes security group if the requesting user has access.
    ---
    tags:
      - security groups
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: security_group_id
        in: path
        type: string
        required: true
        description: ID of target security group.
    responses:
        200:
            description: Security group created.
            schema:
                type: object
                id: ObjectDeleted
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        so = server_ops(auth)
        security_group_delete = {}
        # check project_id
        validate_project(project_id, auth)
        security_group_delete['project_id'] = project_id
        # check security_group_id
        security_group_details = validate_security_group(security_group_id, project_id, auth)
        security_group_delete['sec_group_id'] = security_group_id
        security_group_info = so.delete_sec_group(security_group_delete)
        # check delete success
        if security_group_info == "OK":
            security_group =    {
                                    'name': security_group_details['sec_group_name'],
                                    'id':   security_group_details['sec_group_id']
                                }
            return jsonify({'security_group': security_group})
        else:
            abort(500, 'Internal error. Unable to delete security group %s.' %(security_group_id))
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred deleting security group %s.' %(fe, security_group_id))


# --- Security Keys ----

# get all in cloud
@app.route('/v1.0/security_keys', methods=['GET'])
def get_all_security_keys():
    """
    Lists all security keys.
    Only returns security keys to which the requesting user has access.
    ---
    tags:
      - security keys
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
    responses:
        200:
            description: Security keys listed.
            schema:
                type: array
                id: SecurityKeys
                items:
                    schema:
                        type: object
                        id: SecurityKey
                        required:
                          - name
                          - id
                        properties:
                            name:
                                type: string
                                description: name of security key
                                default: Security_Key_1
                            id:
                                type: string
                                description: ID of security key
                                default: a1:23:45:b6:78:90:12:34:5c:d6:e7:fa:bc:de:fa:89
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        so = server_ops(auth)
        to = tenant_ops(auth)
        security_keys = []
        security_key_info = so.list_sec_keys(auth['project_id'])
        # normalize output
        for info in security_key_info:
            security_key =    {
                                    'name': info['key_name'],
                                    'id':   info['key_id']
                                }
            security_keys.append(security_key)
        return jsonify({'security_keys': security_keys})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred listing security keys.' %(fe))


# get all in project
@app.route('/v1.0/<string:project_id>/security_keys', methods=['GET'])
def get_security_keys(project_id):
    """
    Lists all security keys in a project specified by ID.
    Only returns security keys to which the requesting user has access.
    ---
    tags:
      - security keys
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
    responses:
        200:
            description: Security keys listed.
            schema:
                type: array
                id: SecurityKeys
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        so = server_ops(auth)
        # check project_id
        validate_project(project_id, auth)
        security_keys = []
        security_key_info = so.list_sec_keys(project_id)
        # normalize output
        for info in security_key_info:
            security_key =    {
                                    'name': info['key_name'],
                                    'id':   info['key_id']
                                }
            security_keys.append(security_key)
        return jsonify({'security_keys': security_keys})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred listing security keys in project %s.' %(fe, project_id))


# get
@app.route('/v1.0/<string:project_id>/security_keys/<string:security_key_id>', methods=['GET'])
def get_security_key(project_id, security_key_id):
    """
    Gets detailed information about a specified security key by ID.
    Only returns security key information to which the requesting user has access.
    ---
    tags:
      - security keys
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: security_key_id
        in: path
        type: string
        required: true
        description: ID of target security key
    responses:
        200:
            description: Security keys listed.
            schema:
                type: object
                id: SecurityKeyDetails
                required:
                  - name
                  - id
                  - username
                  - user_id
                  - rsa_public_key
                properties:
                    name:
                        type: string
                        description: name of security key
                        default: Security_Key_1
                    id:
                        type: string
                        description: ID of security key
                        default: a1:23:45:b6:78:90:12:34:5c:d6:e7:fa:bc:de:fa:89
                    username:
                        type: string
                        description: username of security key's owner
                        default: User_1
                    user_id:
                        type: string
                        description: ID of security key's owner
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    rsa_private_key:
                        type: string
                        description: security key's RSA private key
        400:
            description: Bad request.
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        # check project_id
        validate_project(project_id, auth)
        # check security_key_id
        security_key_info = validate_security_key(security_key_id, project_id, auth)
        # normalize output
        security_key =  {
                            'name':             security_key_info['sec_key_name'],
                            'id':               security_key_info['sec_key_id'],
                            'username':         security_key_info['user_name'],
                            'user_id':          security_key_info['user_id'],
                            'rsa_private_key':  security_key_info['public_key']
                        }
        return jsonify({'security_key': security_key})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred getting details for security key %s.' %(fe, security_key_id))


# create
@app.route('/v1.0/<string:project_id>/security_keys', methods=['POST'])
def create_security_key(project_id):
    """
    Creates a security key within a specified project.
    Only creates security key if the requesting user has access.
    ---
    tags:
      - security keys
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: security_key_parameters
        in: body
        description: parameters for security key creation
        required: true
        schema:
            id: SecurityKeyParameters
            type: object
            required:
              - name
            properties:
                name:
                    type: string
                    description: name for security key
                    default: Security_Key_1
    responses:
        200:
            description: Security key created.
            schema:
                type: object
                id: SecurityKeyCreated
                required:
                    - name
                    - id
                properties:
                    name:
                        type: string
                        description: name of security_key
                        default: Security_Key_1
                    id:
                        type: string
                        description: ID of security_key
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        so = server_ops(auth)
        try:
            data = request.get_data()
            json_data = json.loads(data)
        except:
            abort(400, 'Bad request. Body must be in JSON format.')
        security_key_create = {}
        # check project_id
        validate_project(project_id, auth)
        security_key_create['project_id'] = project_id
        # required
        try:
            security_key_create['key_name'] = json_data['name']
        except:
            abort(400, 'Bad request. Body must contain name.')
        security_key_info = so.create_sec_keys(security_key_create)
        # normalize output
        security_key =  {
                            'name': security_key_info['key_name'],
                            'id':   security_key_info['key_id']
                        }
        return jsonify({'security_key': security_key})
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred creating security key.' %(fe))


# delete
@app.route('/v1.0/<string:project_id>/security_keys/<string:security_key_id>', methods=['DELETE'])
def delete_security_key(project_id, security_key_id):
    """
    Deletes a security key specified by ID.
    Only deletes security key if the requesting user has access.
    ---
    tags:
      - security keys
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: username of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of target project
      - name: security_key_id
        in: path
        type: string
        required: true
        description: ID of target security key.
    responses:
        200:
            description: Security key created.
            schema:
                type: object
                id: ObjectDeleted
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        try:
            username = request.headers.get('username')
            password = request.headers.get('password')
        except:
            abort(400, 'Bad request. Headers must contain username and password.')
        auth = authorize(username, password)
        so = server_ops(auth)
        security_key_delete = {}
        # check project_id
        validate_project(project_id, auth)
        security_key_delete['project_id'] = project_id
        # check security_key_id
        security_key_details = validate_security_key(security_key_id, project_id, auth)
        security_key_delete['sec_key_name'] = security_key_details['sec_key_name']
        security_key_info = so.delete_sec_keys(security_key_delete)
        # check security key delete success
        if security_key_info == "OK":
            security_key =    {
                                    'name': security_key_details['sec_key_name'],
                                    'id':   security_key_details['sec_key_id']
                                }
            return jsonify({'security_key': security_key})
        else:
            abort(500, 'Internal error. Unable to delete security key %s.' %(security_key_id))
    except HTTPException as he:
        raise he
    except Exception as fe:
        print fe
        abort(500, 'Internal error. Error <%s> occurred deleting security key %s.' %(fe, security_key_id))


# --- Helper Functions ----

# check credentials and return auth
def authorize(username, password):
    try:
        a = authorization(username,password)
        auth = a.get_auth()
        if  'token' in auth and auth['token'] == "error":
            abort(401, 'Not authroized. User is orphaned or disabled.')
        if auth is None or auth == "ERROR" or 'token' not in auth or auth['token'] == None or auth['token'] == "":
            abort(401, 'Not authorized. Invalid username and/or password.')
        return auth
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred during authorization.' %(fe))


# check cascading permissions
def validate_permissions(project_id, auth):
    # power users / users
    if auth['is_admin'] == 0 and project_id != auth['project_id']:
        abort(401, 'Not authorized. Users and power users can only access resources within their own projects.')
    # project admins
    elif auth['is_admin'] == 1 and auth['username'] != "admin" and auth['username'] != "shadow_admin":
        to = tenant_ops(auth)
        projects = to.list_all_tenants()
        have_access = False
        for project in projects:
            if project_id == project['project_id']:
                have_access = True
                break
        if have_access is False:
            abort(401, 'Not authorized. Project admins can only access resources within their own projects.')


# check if really exists
def validate_shadow(component, function, *args):
    shadow_auth = extras.shadow_auth()
    comp = component(shadow_auth)
    try:
        ret_val = function(comp,*args)
    except:
        abort(401, 'Not authorized. Resource not within own projects.')
    if ret_val is not None:
        abort(401, 'Not authorized. Resource not within own projects.')


# check project_id and return project_info
def validate_project(project_id, auth):
    try:
        to = tenant_ops(auth)
        project_info = to.get_tenant(project_id)
        if project_info is None:
            validate_shadow(tenant_ops, tenant_ops.get_tenant, project_id)
            abort(404, 'Not found. Could not find project %s.' %(project_id))
        validate_permissions(project_id, auth)
        return project_info
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred during project_id validation.' %(fe))


# check instance_id and return instance_info
def validate_instance(instance_id, project_id, auth):
    try:
        so = server_ops(auth)
        server_get =    {
                            'server_id':    instance_id,
                            'project_id':   project_id
                        }
        try:
            instance_info = so.get_server(server_get)
        except:
            validate_shadow(server_ops, server_ops.get_server, server_get)
            abort(404, 'Not found. Could not find instance %s in project %s.' %(instance_id, project_id))
        validate_permissions(project_id, auth)
        return instance_info
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred during instance_id validation.' %(fe))


# check floating_ip_id and return floating_ip_info
def validate_floating_ip(floating_ip_id, auth):
    try:
        l3 = layer_three_ops(auth)
        floating_ip_info = l3.get_floating_ip(floating_ip_id)
        if floating_ip_info is None:
            validate_shadow(layer_three_ops, layer_three_ops.get_floating_ip, floating_ip_id)
            abort(404, 'Not found. Could not find floating IP %s.' %(floating_ip_id))
        validate_permissions(floating_ip_info['project_id'], auth)
        return floating_ip_info
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred validating floating IP %s.' %(fe, floating_ip_id))

# check volume_id and return volume_info
def validate_volume(volume_id, project_id, auth):
    try:
        vo = volume_ops(auth)
        volume_get =    {
                            'volume_id':    volume_id,
                            'project_id':   project_id
                        }
        volume_info = vo.get_volume_info(volume_get)
        if volume_info is None:
            validate_shadow(volume_ops, volume_ops.get_volume_info, volume_get)
            abort(404, 'Not found. Could not find volume %s in project %s.' %(volume_id, project_id))
        validate_permissions(project_id, auth)
        return volume_info
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred during volume_id validation.' %(fe))


# check snapshot_id and return snapshot_info
def validate_volume_snapshot(snapshot_id, auth):
    try:
        vso = snapshot_ops(auth)
        snapshot_info = vso.get_snapshot(snapshot_id)
        if snapshot_info is None:
            validate_shadow(snapshot_ops, snapshot_ops.get_snapshot, snapshot_id)
            abort(404, 'Not found. Could not find volume snapshot %s.' %(snapshot_id))
        validate_permissions(snapshot_info['project_id'], auth)
        return snapshot_info
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred during volume snapshot_id validation.' %(fe))


# check network_id and return network_info
def validate_network(network_id, auth):
    try:
        nno = neutron_net_ops(auth)
        network_info = nno.get_network(network_id)
        if network_info is None:
            validate_shadow(neutron_net_ops, neutron_net_ops.get_network, network_id)
            abort(404, 'Not found. Could not find network %s.' %(network_id))
        if network_info['net_shared'] == "false":
            validate_permissions(network_info['project_id'], auth)
        return network_info
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred during network validation.' %(fe))


# check router_id and return router_info
def validate_router(router_id, auth):
    try:
        l3 = layer_three_ops(auth)
        router_info = l3.get_router(router_id)
        if router_info is None:
            validate_shadow(layer_three_ops, layer_three_ops.get_router, router_id)
            abort(404, 'Not found. Could not find router %s.' %(router_id))
        if 'network_id' in router_info and router_info['network_id'] is not None and router_info['network_id'] != "":
            validate_network(router_info['network_id'], auth)
        else:
            validate_permissions(router_info['project_id'], auth)
        return router_info
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred during router validation.' %(fe))


# check user_id and return user_info
def validate_user(user_id, project_id, auth):
    try:
        uo = user_ops(auth)
        user_get =  {
                        'user_id':      user_id,
                        'project_id':   project_id
                    }
        user_info = uo.get_user_id_info(user_get)
        if user_info is None:
            validate_shadow(user_ops, user_ops.get_user_id_info, user_get)
            abort(404, 'Not found. Could not find user %s in project %s.' %(user_id, project_id))
        validate_permissions(project_id, auth)
        return user_info
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred during user validation.' %(fe))


# check security_group_id and return security_group_info
def validate_security_group(security_group_id, project_id, auth):
    try:
        so = server_ops(auth)
        security_group_get =    {
                                    'sec_group_id': security_group_id,
                                    'project_id':   project_id
                                }
        try:
            security_group_info = so.get_sec_group(security_group_get)
        except:
            validate_shadow(server_ops, server_ops.get_sec_group, security_group_get)
            abort(404, 'Not found. Could not find security group %s in project %s.' %(security_group_id, project_id))
        validate_permissions(project_id, auth)
        return security_group_info
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred during security group validation.' %(fe))


# check ports format
def validate_ports(ports):
    try:
        for port in ports:
            port_parts = port.split('-')
            if len(port_parts) != 1 and len(port_parts) != 2:
                abort(400, 'Bad request. Improper ports format. Specified ports must be indiviual ports or port ranges.')
            if len(port_parts) == 2:
                if int(port_parts[0]) > int(port_parts[1]):
                    abort(400, 'Bad request. Improper ports format. Ranged ports must be of the form <min>-<max>.')
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred during port format validation.' %(fe))


# check security_key_id and return security_key_info
def validate_security_key(security_key_id, project_id, auth):
    try:
        so = server_ops(auth)
        security_key_get =  {
                                'sec_key_id':   security_key_id,
                                'project_id':   project_id
                            }
        security_key_info = so.get_sec_keys(security_key_get)
        if security_key_info is None:
            validate_shadow(server_ops, server_ops.get_sec_keys, security_key_get)
            abort(404, 'Not found. Could not find security key %s in project %s.' %(security_key_id, project_id))
        validate_permissions(project_id, auth)
        return security_key_info
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred during security key validation.' %(fe))


# check image_id and return image_info
def validate_image(image_id, auth):
    try:
        go = glance_ops(auth)
        try:
            image_info = go.get_image(image_id)
        except:
            validate_shadow(glance_ops, glance_ops.get_image, image_id)
            abort(404, 'Not found. Could not find image %s.' %(image_id))
        if image_info['visibility'] == "private":
            validate_permissions(image_info['project_id'], auth)
        return image_info
    except HTTPException as he:
        raise he
    except Exception as fe:
        abort(500, 'Internal error. Error <%s> occurred during image_id validation.' %(fe))


# --- App ----

if __name__ == '__main__':
    app.run(host=api_ip, port=6969, debug=True)

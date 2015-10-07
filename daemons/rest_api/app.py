# base
import ast, json, sys
# flask
from flask import Flask, jsonify, abort, make_response, request
from werkzeug.exceptions import HTTPException
from flasgger import Swagger
# django
from django.conf import settings
from transcirrus.interfaces.Coalesce import settings as tc_settings
settings.configure(default_settings=tc_settings, DEBUG=True, LOGGING_CONFIG=None, DATABASE_ROUTERS=[], USE_TZ=False, DEFAULT_INDEX_TABLESPACE="", CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',}},
                   DEFAULT_TABLESPACE="", USE_L10N=True, LOCALE_PATHS=(), FORMAT_MODULE_PATH=None, DEFAULT_CHARSET="utf-8", DEFAULT_CONTENT_TYPE="text/html")
sys.path.append("/usr/local/lib/python2.7/transcirrus/interfaces/Coalesce/")
from transcirrus.interfaces.Coalesce.coalesce.coal_beta import views
# common
from transcirrus.common import util
from transcirrus.common.auth import authorization
from transcirrus.common import extras
# projects
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.operations import build_complete_project
# instances
from transcirrus.component.nova.server import server_ops
from transcirrus.operations import boot_new_instance as boot_from_vol_ops
# flavors
from transcirrus.component.nova.flavor import flavor_ops
# floating ips
from transcirrus.component.neutron.layer_three import layer_three_ops
# volumes
from transcirrus.component.cinder.cinder_volume import volume_ops
# networks
from transcirrus.component.neutron.network import neutron_net_ops


# --- API Setup ----

app = Flask(__name__)
Swagger(app)
node_id = util.get_node_id()
api_ip = util.get_system_variables(node_id)['MGMT_IP']


# --- Error Handlers ----

# 400, bad request
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': {'message': "Bad Request.  Check your request parameters", 'number': 400}}), 400)


# 401, not authorized
@app.errorhandler(401)
def not_authorized(error):
    return make_response(jsonify({'error': {'message': "Not authorized.  Check your credentials and user privileges.", 'number': 401}}), 401)


# 404, not found
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': {'message': "Not found.", 'number': 404}}), 404)


# 500, internal server error
@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': {'message': "Internal server error.", 'number': 500}}), 500)


# --- Version Info ----

# get
@app.route('/v1.0/version', methods=['GET'])
def get_version():
    request = ""
    ver_json = views.get_version(request)
    ver_dict = ast.literal_eval(ver_json.content)
    version = {'release': ver_dict['data']['release'], 'major': ver_dict['data']['major'], 'full_str': ver_dict['data']['full_str'], 'short_str': ver_dict['data']['short_str'], 'minor': ver_dict['data']['minor']}
    return jsonify({'version': version})


# --- Projects ----

# get all
@app.route('/v1.0/projects', methods=['GET'])
def get_projects():
    """
    Lists all projects.
    Only returns projects to which the specified user has access.
    ---
    tags:
      - projects
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: useranme of user making request
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
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        to = tenant_ops(auth)
        projects = []
        if auth['is_admin'] == 1:
            projects = to.list_all_tenants()
        else:
            project = to.get_tenant(auth['project_id'])
            projects = [{
                            'name': project['project_name'],
                            'id':   project['project_id']
                       }]
        projects[:] = [p for p in projects if p.get('project_name') != "trans_default"]
        return jsonify({'projects': projects})
    except HTTPException as e:
        raise e
    except:
        abort(500)


# get
@app.route('/v1.0/projects/<string:project_id>', methods=['GET'])
def get_project(project_id):
    """
    Gets detailed information about a specified project by ID.
    Only returns project information to which the specified user has access.
    ---
    tags:
      - projects
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: useranme of user making request
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
                        description: ip address of host system
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
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        to = tenant_ops(auth)
        project_info = to.get_tenant(project_id)
        if project_info is not None:
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
        else:
            abort(404)
    except HTTPException as e:
        raise e
    except Exception as fe:
        print fe
        abort(500)


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
        description: useranme of user making request
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
                admin_username:
                    type: string
                    description: username for project admin
                    default: Admin_Project_1
                admin_password:
                    type: string
                    description: password for project admin
                    default: password
                admin_email:
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
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        data = request.get_data()
        json_data = json.loads(data)
        project_name = json_data['name']
        admin_username = json_data['admin_username']
        admin_password = json_data['admin_password']
        admin_email = json_data['admin_email']
        security_group_name = json_data['security_group_name']
        security_key_name = json_data['security_key_name']
        network_name = json_data['network_name']
        router_name = json_data['router_name']
        dns_address = []
        dns_address.append(json_data['dns_address'])
        project_create =   {
                                'project_name':     project_name,
                                'user_dict':        {
                                                        'username':     admin_username,
                                                        'password':     admin_password,
                                                        'user_role':    "admin",
                                                        'email':        admin_email,
                                                        'project_id':   ""
                                                    },
                                'net_name':         network_name,
                                'subnet_dns':       dns_address,
                                'sec_group_dict':   {
                                                        'ports':        "",
                                                        'group_name':   security_group_name,
                                                        'group_desc':   "none",
                                                        'project_id':   ""
                                                    },
                                'sec_keys_name':    security_key_name,
                                'router_name':      router_name
                            }
        project_id = build_complete_project.build_project(auth, project_create)
        project =   {
                        'name': project_name,
                        'id':   project_id
                    }
        return jsonify({'project': project})
    except HTTPException as e:
        raise e
    except Exception as fe:
        print fe
        abort(500)


# --- Instances ----

# get all in cloud
@app.route('/v1.0/instances', methods=['GET'])
def get_all_instances():
    """
    Lists all instances in cloud.
    Only returns instances to which the specified user has access.
    ---
    tags:
      - instances
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: useranme of user making request
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
                                description: floating ip address of instance
                                default: 127.0.0.1
                            status:
                                type: string
                                description: status of instance
                                default: ACTIVE
                            zone:
                                type: string
                                description: availability zone of instance
                                default: nova
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        so = server_ops(auth)
        instances = []
        if auth['is_admin'] == 1:
            instances_info = so.list_all_servers()
        else:
            instances_info = so.list_servers()
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
    except HTTPException as e:
        raise e
    except:
        abort(500)


# get all in project
@app.route('/v1.0/<string:project_id>/instances', methods=['GET'])
def get_instances(project_id):
    """
    Lists all instances in specified project.
    Only returns instances to which the specified user has access.
    ---
    tags:
      - instances
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: useranme of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of project the instance resides in
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
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        so = server_ops(auth)
        instances = []
        instances_info = so.list_servers(project_id)
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
    except HTTPException as e:
        raise e
    except:
        abort(500)


# get
@app.route('/v1.0/<string:project_id>/instances/<string:instance_id>', methods=['GET'])
def get_instance(project_id, instance_id):
    """
    Gets detailed information about a specified instance by ID.
    Only returns project information to which the specified user has access.
    ---
    tags:
      - instances
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: useranme of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of project the instance resides in
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
                    - boot_from_volume
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
                              - InternalNetworks
                              - ExternalNetworks
                            properties:
                                InternalNetworks:
                                    type: array
                                    items:
                                        schema:
                                            type: object
                                            id: InternalNetwork
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
                                                    description: ip address of instance
                                                    default: 10.0.1.7
                                                version:
                                                    type: integer
                                                    description: ip version
                                                    default: 4
                                ExternalNetworks:
                                    type: array
                                    items:
                                        schema:
                                            type: object
                                            id: ExternalNetwork
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
                                                    description: ip address of instance
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
                        description: floating ip address of instance
                        default: 127.0.0.1
                    floating_ip_id:
                        type: string
                        description: ID of instance's floating ip address
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    novnc_console:
                        type: string
                        description: url of instance's novnc console
                        default: http://127.0.0.1:6080/vnc_auto.html?token=1234a56b-8901-2345-67c8-90de12f34ab5
                    date_created:
                        type: string
                        description: date of instance creation
                        default: "2015-10-02T19:28:33Z"
                    boot_from_volume:
                        type: boolean
                        description: conveying if instance boots from volume
                        default: false
                    fault:
                        type: string
                        description: fault of instance
                        default: None
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        so = server_ops(auth)
        nno = neutron_net_ops(auth)
        server_get =    {
                            'server_id':    instance_id,
                            'project_id':   project_id
                        }
        instance_info = []
        instance_info = so.get_server(server_get)
        print instance_info
        internal = []
        external = []
        if 'server_net_id' in instance_info:
            net_id = instance_info['server_net_id']
            net_name = nno.get_network(net_id)['net_name']
            for info in instance_info['server_int_net'][net_name]:
                if info['OS-EXT-IPS:type'] == "fixed":
                    info['name'] = net_name
                    info['id'] = net_id
                    internal.append(info)
                elif info['OS-EXT-IPS:type'] == "floating":
                    info['name'] = net_name
                    info['id'] = net_id
                    external.append(info)
            boot_from_volume = False
            if 'boot_from_vol' in instance_info and instance_info['boot_from_vol'] == "true":
                boot_from_volume = True
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
                            'boot_from_volume':     boot_from_volume
                       }
            return jsonify({'instance': instance})
        else:
            abort(404)
    except HTTPException as e:
        raise e
    except Exception as fe:
        print fe
        abort(500)


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
        description: useranme of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of project the instance will reside in
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
                boot_from_volume:
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
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        data = request.get_data()
        json_data = json.loads(data)
        instance_create = {}
        # required
        instance_create['project_id'] = project_id
        instance_create['instance_name'] = json_data['name']
        instance_create['image_id'] = json_data['image_id']
        instance_create['flavor_id'] = json_data['specification_id']
        instance_create['sec_group_name'] = json_data['security_group_name']
        instance_create['sec_key_name'] = json_data['security_key_name']
        # optional
        if 'network_name' in json_data:
            instance_create['network_name'] = json_data['network_name']
        if 'zone' in json_data:
            instance_create['avail_zone'] = json_data['zone']
        if 'boot_from_volume' in json_data:
            instance_create['boot_from_vol'] = json_data['boot_from_volume']
        if 'volume_size' in json_data:
            instance_create['volume_size'] = json_data['volume_size']
        if 'volume_name' in json_data:
            instance_create['volume_name'] = json_data['volume_name']
        if 'volume_type' in json_data:
            instance_create['volume_type'] = json_data['volume_type']
        instance_info = boot_from_vol_ops.boot_instance(instance_create, auth)['instance']
        instance =  {
                        'name':                 instance_info['vm_name'],
                        'id':                   instance_info['vm_id'],
                        'security_key_name':    instance_info['sec_key_name'],
                        'security_group_name':  instance_info['sec_group_name'],
                        'project_id':           instance_info['project_id'],
                        'username':             instance_info['created_by'],
                    }
        return jsonify({'instance': instance})
    except HTTPException as e:
        raise e
    except Exception as fe:
        print fe
        abort(500)


# delete
@app.route('/v1.0/<string:project_id>/instances/<string:instance_id>', methods=['DELETE'])
def delete_instance(project_id, instance_id):
    """
    Deletes a specified instance by ID.
    Only able to delete if specified user has access.
    ---
    tags:
      - instances
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: useranme of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of project the instance resides in
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
                  - status
                properties:
                    id:
                        type: string
                        description: ID of target object
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
                    status:
                        type: string
                        description: OK if success, ERROR if failure
                        default: OK
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        so = server_ops(auth)
        instance_delete =   {
                                'project_id':   project_id,
                                'server_id':    instance_id
                            }
        instance_info = so.delete_server(instance_delete)
        instance =  {
                        'id':       instance_id,
                        'status':   instance_info
                    }
        return jsonify({'instance': instance})
    except HTTPException as e:
        raise e
    except Exception as fe:
        print fe
        abort(500)


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
        description: useranme of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of project the instance specification will reside in
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
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        data = request.get_data()
        json_data = json.loads(data)
        instance_specification_create = {}
        # required
        instance_specification_create['name'] = json_data['name']
        instance_specification_create['ram'] = json_data['ram']
        instance_specification_create['boot_disk'] = json_data['disk']
        instance_specification_create['cpus'] = json_data['cpus']
        # optional
        if 'visibility' in json_data and json_data['visibility'] == "public":
            instance_specification_create['public'] = "True"
        fo = flavor_ops(auth)
        instance_specification_info = fo.create_flavor(instance_specification_create)
        instance_specification =    {
                                        'id':   instance_specification_info['flav_id'],
                                        'name': instance_specification_info['flavor_name']
                                    }
        return jsonify({'instance_specification': instance_specification})
    except HTTPException as e:
        raise e
    except Exception as fe:
        print fe
        abort(500)


# --- Floating IPs ----

# get all
@app.route('/v1.0/floating_ips', methods=['GET'])
def get_floating_ips():
    """
    Lists all floating IPs.
    Only returns floating IPs to which the specified user has access.
    ---
    tags:
      - floating ips
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: useranme of user making request
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
                          - in_use
                        properties:
                            address:
                                type: string
                                description: address of floating IP
                                default: 127.0.0.1
                            id:
                                type: string
                                description: ID of floating IP
                                default: 1234a56b-8901-2345-67c8-90de12f34ab5
                            in_use:
                                type: boolean
                                description: conveying if floating IP is in use
                                default: false

        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        l3 = layer_three_ops(auth)
        floating_ips = []
        floating_ips_info = l3.list_floating_ips()
        for info in floating_ips_info:
            floating_ip =   {
                                "address":   info['floating_ip'],
                                "id":        info['floating_ip_id']
                            }
            if info['floating_in_use'] == "true":
                floating_ip['in_use'] = True
            else:
                floating_ip['in_use'] = False
            floating_ips.append(floating_ip)
        return jsonify({'floating_ips': floating_ips})
    except HTTPException as e:
        raise e
    except:
        abort(500)


# get
@app.route('/v1.0/floating_ips/<string:floating_ip_id>', methods=['GET'])
def get_floating_ip(floating_ip_id):
    """
    Gets detailed information about a specified floating IP by ID.
    Only returns floating IP information to which the specified user has access.
    ---
    tags:
      - floating ips
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: useranme of user making request
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
                    - netowrk_id
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
                        description: name of instance to which the floating IP is associated
                        default: Instance_1
                    instance_id:
                        type: string
                        description: ID of instance to which the floating IP is associated
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
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        l3 = layer_three_ops(auth)
        floating_ip_info = l3.get_floating_ip(floating_ip_id)
        if floating_ip_info is not None:
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
        else:
            abort(404)
    except HTTPException as e:
        raise e
    except Exception as fe:
        print fe
        abort(500)


# create
@app.route('/v1.0/floating_ips', methods=['POST'])
def create_floating_ip():
    """
    Creates a floating IP address within a specified project.
    Admin and power user only.
    ---
    tags:
      - floating ips
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: useranme of user making request
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
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        # admin / power user only
        if auth['user_level'] == 2:
            abort(401)
        data = request.get_data()
        json_data = json.loads(data)
        floating_ip_create = {}
        # required
        floating_ip_create['project_id'] = json_data['project_id']
        # optional
        if 'network_id' in json_data:
            floating_ip_create['ext_net_id'] = json_data['network_id']
        else:
            floating_ip_create['ext_net_id'] = util.get_default_pub_net_id()
        l3 = layer_three_ops(auth)
        floating_ip_info = l3.allocate_floating_ip(floating_ip_create)
        floating_ip =   {
                            'address':          floating_ip_info['floating_ip'],
                            'id':               floating_ip_info['floating_ip_id']
                        }
        return jsonify({'floating_ip': floating_ip})
    except HTTPException as e:
        raise e
    except Exception as fe:
        print fe
        abort(500)


# update
@app.route('/v1.0/floating_ips/<string:floating_ip_id>', methods=['PUT'])
def update_floating_ip(floating_ip_id):
    """
    Updates a specified floating IP by ID.
    Associate or disassociate floating IP with an instance.
    Only updates floating IP information to which the specified user has access.
    ---
    tags:
      - floating ips
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: useranme of user making request
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
      - name: floating_ip_update
        in: body
        description: parameters for floating IP update
        required: true
        schema:
            id: FloatingIPUpdate
            type: object
            required:
              - project_id
              - instance_id
              - operation
            properties:
                project_id:
                    type: string
                    description: ID of project in which floating IP resides
                    default: abcd12e3f456789012345a678b9cde01
                instance_id:
                    type: string
                    description: ID of instance to associate with the floating IP
                    default: 1234a56b-8901-2345-67c8-90de12f34ab5
                operation:
                    type: string
                    description: add to associate, remove to disassociate
                    default: add
    responses:
        200:
            description: Floating IP updated.
            schema:
                type: object
                id: FloatingIPUpdated
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
                        description: name of instance to which the floating IP is associated
                        default: Instance_1
                    instance_id:
                        type: string
                        description: ID of instance to which the floating IP is associated
                        default: 1234a56b-8901-2345-67c8-90de12f34ab5
        400:
            description: Bad request.
        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        data = request.get_data()
        json_data = json.loads(data)
        floating_ip_update = {}
        # required
        floating_ip_update['project_id'] = json_data['project_id']
        floating_ip_update['instance_id'] = json_data['instance_id']
        # check operation
        if json_data['operation'] != "add" and json_data['operation'] != "remove":
            abort(400)
        floating_ip_update['action'] = json_data['operation']
        l3 = layer_three_ops(auth)
        floating_ip_update['floating_ip'] = l3.get_floating_ip(floating_ip_id)['floating_ip']
        floating_ip_info = l3.update_floating_ip(floating_ip_update)
        print floating_ip_info
        floating_ip =   {
                            'address':          floating_ip_info['floating_ip'],
                            'id':               floating_ip_info['floating_ip_id'],
                            'instance_name':    floating_ip_info['instance_name'],
                            'instance_id':      floating_ip_info['instance_id']
                        }
        return jsonify({'floating_ip': floating_ip})
    except HTTPException as e:
        raise e
    except Exception as fe:
        print fe
        abort(500)


# delete
@app.route('/v1.0/floating_ips/<string:floating_ip_id>', methods=['DELETE'])
def delete_floating_ip(floating_ip_id):
    """
    Deletes a specified floating IP by ID.
    Admin and power user only.
    ---
    tags:
      - floating ips
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: useranme of user making request
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
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        # admin / power user only
        if auth['user_level'] == 2:
            abort(401)
        l3 = layer_three_ops(auth)
        floating_ip_delete = l3.get_floating_ip(floating_ip_id)
        floating_ip_info = l3.deallocate_floating_ip(floating_ip_delete)
        floating_ip =   {
                            'id':               floating_ip_id,
                            'status':           floating_ip_info
                        }
        return jsonify({'floating_ip': floating_ip})
    except HTTPException as e:
        raise e
    except Exception as fe:
        print fe
        abort(500)


# --- Volumes ----

# get all in cloud
@app.route('/v1.0/volumes', methods=['GET'])
def get_volumes():
    """
    Lists all volumes.
    Only returns volumes to which the specified user has access.
    ---
    tags:
      - volumes
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: useranme of user making request
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
                                description: ssd or spindle
                                default: ssd
                            project_id:
                                type: string
                                description: ID of volumes's project
                                default: abcd12e3f456789012345a678b9cde01

        401:
            description: Not authorized.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        vo = volume_ops(auth)
        volumes = []
        volumes_info = vo.list_volumes()
        for info in volumes_info:
            volume =    {
                            "name":         info['volume_name'],
                            "id":           info['volume_id'],
                            "type":         info['volume_type'],
                            "project_id":   info['project_id']
                        }
            volumes.append(volume)
        return jsonify({'volumes': volumes})
    except HTTPException as e:
        raise e
    except:
        abort(500)


# get
@app.route('/v1.0/<string:project_id>/volumes/<string:volume_id>', methods=['GET'])
def get_volume(project_id, volume_id):
    """
    Gets detailed information about a specified volume by ID.
    Only returns volume information to which the specified user has access.
    ---
    tags:
      - volumes
    parameters:
      - name: username
        in: header
        type: string
        required: true
        description: useranme of user making request
      - name: password
        in: header
        type: string
        required: true
        description: password of user making request
      - name: project_id
        in: path
        type: string
        required: true
        description: ID of project the volume resides in
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
                    - mountpoint
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
                        description: ssd or spindle
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
                    mountpoint:
                        type: string
                        description: mountpoint of volume on instance
                        default: /vda
        401:
            description: Not authorized.
        404:
            description: Not found.
        500:
            description: Internal server error.
    """
    try:
        username = request.headers.get('username')
        password = request.headers.get('password')
        auth = authorize(username, password)
        vo = volume_ops(auth)
        volume_get =    {
                            'project_id':   project_id,
                            'volume_id':    volume_id
                        }
        volume_info = vo.get_volume_info(volume_get)
        if volume_info is not None:
            volume =   {
                            'name':             volume_info['volume_name'],
                            'id':               volume_info['volume_id'],
                            'type':             volume_info['volume_type'],
                            'size':             volume_info['volume_size'],
                            'instance_name':    volume_info['volume_instance_name'],
                            'instance_id':      volume_info['volume_instance'],
                            'mountpoint':       volume_info['volume_mount_location']
                        }
            if volume_info['volume_attached'] == "true":
                volume['is_attached'] = True
            else:
                volume['is_attached'] = False
            return jsonify({'volume': volume})
        else:
            abort(404)
    except HTTPException as e:
        raise e
    except Exception as fe:
        print fe
        abort(500)


# --- Helper Functions ----

def authorize(username, password):
    try:
        a = authorization(username,password)
        auth = a.get_auth()
        if auth['token'] != None and auth['token'] != "":
            return auth
        abort(401)
    except:
        abort(401)


if __name__ == '__main__':
    app.run(host=api_ip, port=6969, debug=True)

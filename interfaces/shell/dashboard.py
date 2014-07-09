from __future__ import nested_scopes, division
import sys, os, stat, time, getopt, subprocess, dialog
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.operations.build_complete_project import build_project
from transcirrus.operations.destroy_project import destroy_project
from transcirrus.database import node_db as node_op

progname = os.path.basename(sys.argv[0])
progversion = "0.1"
version_blurb = """Transcirrus CoalesceShell Beta"""

usage = ""

# Global parameters
params = {}


def handle_exit_code(d, code):
    """Sample function showing how to interpret the dialog exit codes.

    This function is not used after every call to dialog in this demo
    for two reasons:

       1. For some boxes, unfortunately, dialog returns the code for
          ERROR when the user presses ESC (instead of the one chosen
          for ESC). As these boxes only have an OK button, and an
          exception is raised and correctly handled here in case of
          real dialog errors, there is no point in testing the dialog
          exit status (it can't be CANCEL as there is no CANCEL
          button; it can't be ESC as unfortunately, the dialog makes
          it appear as an error; it can't be ERROR as this is handled
          in dialog.py to raise an exception; therefore, it *is* OK).

       2. To not clutter simple code with things that are
          demonstrated elsewhere.

    """
    # d is supposed to be a Dialog instance
    if code in (d.DIALOG_CANCEL, d.DIALOG_ESC):
        if code == d.DIALOG_CANCEL:
            msg = "You chose cancel in the last dialog box. Do you want to " \
                  "exit the TransCirrus CoalesceShell?"
        else:
            msg = "You pressed ESC in the last dialog box. Do you want to " \
                  "exit the TransCirrus CoalesceShell?"
        # "No" or "ESC" will bring the user back to the demo.
        # DIALOG_ERROR is propagated as an exception and caught in main().
        # So we only need to handle OK here.
        if d.yesno(msg) == d.DIALOG_OK:
            clear_screen(d)
            sys.exit(0)
        return d.DIALOG_CANCEL
    else:
        # 'code' can be d.DIALOG_OK (most common case) or, depending on the
        # particular dialog box, d.DIALOG_EXTRA, d.DIALOG_HELP,
        # d.DIALOG_ITEM_HELP... (cf. _dialog_exit_status_vars in dialog.py)
        return code


def dashboard(d):
    while True:
        (code, tag) = d.radiolist(
            "Dashboard - Select Component to Manage",
            width=65,
            choices=[("Nodes", "List and manage nodes", 1),
                     ("Projects", "List and manage projects", 0),
                     ("Users", "List and manage users", 0)])
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag


def nodes(d, nodeList):
    delChoice = ("Remove", "Remove Node from Cloud", 0)
    dashChoice = ("Dashboard", "Return to Dashboard", 1)
    allChoices = []
    counter = 0
    for entry in nodeList:
        if(entry == "OK"):
            continue
        counter += 1
        choice = (str(counter), entry['node_type'] + ": " + entry['node_name'], 0)
        allChoices.append(choice)
    allChoices.append(delChoice)
    allChoices.append(dashChoice)
    while True:
        (code, tag) = d.radiolist("Nodes - Select Node to Manage",
        width=65, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def nodeRemove(d, nodeList):
    backChoice = ("Back", "Return to Nodes", 1)
    allChoices = []

    for entry in nodeList:
        allChoices.append(entry)
    allChoices.append(backChoice)
    while True:
        (code, tag) = d.radiolist("Nodes - Select Node to Remove",
        width=65, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag


def nodeDel(d, node):
    return d.yesno("Are you sure you would like to remove this Node?",
         yes_label="Yes, I'm sooo sure",
         no_label="No, not yet", width=80)


def nodeInfo(d, node):
    node_info = node_op.get_node(node['node_id'])
    return d.yesno(("Node Overview\n\n" +
                    "Name:          " + node_info['node_name'] + "\n" +
                    "Id:            " + node['node_id'] + "\n" +
                    "Type:          " + node_info['node_type'] + "\n" +
                    "Data IP:       " + node_info['node_data_ip'] + "\n" +
                    "Management IP: " + node_info['node_mgmt_ip'] + "\n" +
                    "Controller:    " + node_info['node_controller'] + "\n" +
                    "Cloud Name:    " + node_info['node_cloud_name'] + "\n" +
                    "Zone:          " + node_info['availability_zone'] + "\n" +
                    "Fault:         " + node_info['node_fault_flag'] + "\n" +
                    "Ready:         " + node_info['node_ready_flag'] + "\n" +
                    "Gluster Peer:  " + node_info['node_gluster_peer'] + "\n" +
                    "Status:        " + node_info['status']),
                    yes_label="Manage this Node",
                    no_label="Return to Nodes", width=77, height=20)


def nodeManage(d, node):
    node_info = node_op.get_node(node['node_id'])
    while True:
        elements = [
            ("Name:", 1, 1, node_info['node_name'], 1, 24, 16, 16, 0x2),
            ("Id:", 2, 1, node['node_id'], 2, 24, 16, 16, 0x2),
            ("Type:", 3, 1, node_info['node_type'], 3, 24, 16, 16, 0x2),
            ("Data IP:", 4, 1, node_info['node_data_ip'], 4, 24, 16, 16, 0x2),
            ("Management IP:", 5, 1, node_info['node_mgmt_ip'], 5, 24, 16, 16, 0x0),
            ("Controller:", 6, 1, node_info['node_controller'], 6, 24, 16, 16, 0x2),
            ("Cloud Name:", 7, 1, node_info['node_cloud_name'], 7, 24, 16, 16, 0x2),
            ("Zone:", 8, 1, node_info['availability_zone'], 8, 24, 16, 16, 0x2),
            ("Fault:", 9, 1, node_info['node_fault_flag'], 9, 24, 16, 16, 0x2),
            ("Ready:", 10, 1, node_info['node_ready_flag'], 10, 24, 16, 16, 0x2),
            ("Gluster Peer:", 11, 1, node_info['node_gluster_peer'], 11, 24, 16, 16, 0x2),
            ("Status:", 12, 1, node_info['status'], 12, 24, 16, 16, 0x2)]

        (code, fields) = d.mixedform(
            "Update Node Info:", elements, width=77, height=20)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    
    try:
        n_name, n_id, n_type, n_data, mgmt_ip, n_controller, n_cloud, n_zone, n_fault, n_ready, n_gluster, n_status = fields
        d.msgbox(mgmt_ip)
        update_dict = {'node_id': node['node_id'], 'node_mgmt_ip': mgmt_ip}
        upd = node_op.update_node(update_dict)
        d.msgbox(upd)
    except Exception as e:
        print e

    return

def projects(d, projectList):
    addChoice = ("Add", "Add a Project", 0)
    dashChoice = ("Dashboard", "Return to Dashboard", 1)
    allChoices = []
    counter = 0
    for entry in projectList:
        counter += 1
        choice = (str(counter), entry['project_name'], 0)
        allChoices.append(choice)
    allChoices.append(addChoice)
    allChoices.append(dashChoice)
    while True:
        (code, tag) = d.radiolist("Projects - Select Project to Manage",
        width=80, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def users(d, userList):
    addChoice = ("Add", "Add a User", 0)
    #delChoice = ("Remove", "Remove a User", 0)
    dashChoice = ("Dashboard", "Return to Dashboard", 1)
    allChoices = []
    counter = 0
    for entry in userList:
        counter += 1
        choice = (str(counter), entry['name'], 0)
        allChoices.append(choice)
    allChoices.append(addChoice)
    #allChoices.append(delChoice)
    allChoices.append(dashChoice)
    while True:
        (code, tag) = d.radiolist("Users - Select User to Manage",
        width=65, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

"""
def userRemove(d, userList):
    backChoice = ("Back", "Return to Users", 1)
    allChoices = []
    counter = 0

    for entry in userList:
        counter+=1
        choice = (str(counter), entry['name'], 0)
        allChoices.append(choice)
    allChoices.append(backChoice)
    while True:
        (code, tag) = d.radiolist("Users - Select User to Remove",
        width=65, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag
"""

def projectAdd(d, auth_dict):

    while True:
        HIDDEN = 0x1
        elements = [
            ("Project Name:", 1, 1, "", 1, 32, 40, 40, 0x0),
            ("Project Power-User Name:", 2, 1, "", 2, 32, 40, 40, 0x0),
            ("Project Power-User Password:", 3, 1, "", 3, 32, 40, 40, HIDDEN),
            ("Re-Enter Power-User Password:", 4, 1, "", 4, 32, 40, 40, HIDDEN),
            ("Project Power-User Email:", 5, 1, "", 5, 32, 40, 40, 0x0),
            ("Net Name:", 6, 1, "", 6, 32, 40, 40, 0x0),
            ("Subnet DNS:", 7, 1, "", 7, 32, 40, 40, 0x0),
            ("Ports:", 8, 1, "", 8, 32, 40, 40, 0x0),
            ("Security Group Name:", 9, 1, "", 9, 32, 40, 40, 0x0),
            ("Security Group Description:", 10, 1, "", 10, 32, 40, 40, 0x0),
            ("Security Keys Name:", 11, 1, "", 11, 32, 40, 40, 0x0),
            ("Router Name:", 12, 1, "", 12, 32, 40, 40, 0x0)]

        (code, fields) = d.mixedform(
            "Please fill in Project Information:", elements, width=90, insecure=True)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
        if handle_exit_code(d, code) == d.DIALOG_CANCEL:
            return
    project_name, username, password, email, net_name, subnet_dns, ports, group_name, group_desc, sec_keys_name, router_name = fields
    if(project_name == "" or username == "" or password == "" or confirm == "" or email == "" or net_name == "" or subnet_dns == "" or ports == "" or group_name == "" or group_desc == "" or sec_keys_name == "" or router_name == ""):
        d.msgbox("All fields are required, try again.")
        return "Add"
    if(password != confirm):
        d.msgbox("Passwords did not match, try again.")
        return "Add"
    user_dict = {"username":username, "password":password, "user_role":"pu", "email":email, "project_id": None}
    sec_group_dict = {"ports":None, "group_name":group_name, "group_desc":group_desc, "project_id": None}
    project_dict = {"project_name":project_name, "user_dict":user_dict, "net_name":net_name, "subnet_dns":[], "sec_group_dict":sec_group_dict, "sec_keys_name":sec_keys_name, "router_name":router_name}
    project = build_project(auth_dict, project_dict)
    return "Projects"


def projectDel(d, auth_dict, project):
    yesno =  d.yesno("Are you sure you would like to delete this Project?",
         yes_label="Yes, I'm sooo sure",
         no_label="No, not yet", width=80)
    
    if(yesno == d.DIALOG_OK):
        project_dict = {"project_id":project['project_id'], "project_name":project['project_name'], "keep_users":False}
        destroy_project(auth_dict, project_dict)
        
    return yesno


def projectInfo(d, project):
    return d.yesno(("Overview\n\n" + project['project_name']),
    yes_label="Manage this Project",
    no_label="Return to Projects", width=50)


def projectManage(d, project):
    while True:
        (code, tag) = d.radiolist(
            project['project_name'] + " - Select Component to Manage",
            width=65,
            choices=[("Users", "List and manage users", 0),
                     ("Instances", "List and manage instances", 0),
                     ("Volumes", "List and manage volumes", 0),
                     ("Containers", "List and manage containers", 0),
                     ("Snapshots", "List and manage snapshots", 0),
                     ("Images", "List and manage images", 0),
                     ("Security Groups", "List and manage security groups", 0),
                     ("Keypairs", "List and manage keypairs", 0),
                     ("Networks", "Display and manage network", 0),
                     ("Rename", "Rename this project", 0),
                     ("Delete", "Completely remove this project", 0),
                     ("Back", "Return to project info", 1)])
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def projectRename(d, tenant_op, project):
    HIDDEN = 0x1
    while True:
        elements = [
            ("Name:", 1, 1, project['project_name'], 1, 32, 40, 40, 0x0)]

        (code, name) = d.mixedform(
            "Rename Project:", elements, insecure=True, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    project_name = name
    if(project_name == ""):
        d.msgbox("Name cannot be blank, try again.")
        return "Rename"
    return "OK"


def projUsers(d, tenant_op, project):
    addChoice = ("Add", "Add a User", 0)
    projChoice = ("Back", "Return to Project Components", 1)
    allChoices = []
    counter = 0
    userList = tenant_op.list_tenant_users(project['project_id'])
    for entry in userList:
        counter += 1
        choice = (str(counter), entry['username'], 0)
        allChoices.append(choice)
    allChoices.append(addChoice)
    allChoices.append(projChoice)
    while True:
        (code, tag) = d.radiolist(project['project_name'] + " - Select User to Manage",
        width=65, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag


def userAdd(d, user_op, project):
    HIDDEN = 0x1
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 32, 40, 40, 0x0),
            ("Password:", 2, 1, "", 2, 32, 40, 40, HIDDEN),
            ("Re-Enter Password:", 3, 1, "", 3, 32, 40, 40, HIDDEN),
            ("Role (admin/pu/user):", 4, 1, "", 4, 32, 40, 40, 0x0),
            ("Email", 5, 1, "", 5, 32, 40, 40, 0x0)]

        (code, fields) = d.mixedform(
            "Add User:", elements, width=90, insecure=True)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
        if handle_exit_code(d, code) == d.DIALOG_CANCEL:
            return
    username, password, confirm, user_role, email = fields
    if(username == "" or password == "" or confirm == "" or user_role == "" or email == ""):
        d.msgbox("All fields are required, try again.")
        return "Add"
    if(password != confirm):
        d.msgbox("Passwords did not match, try again.")
        return "Add"
    if(user_role != "admin" and user_role != "pu" and user_role != "user"):
        d.msgbox("Role must be admin, pu or user, try again.")
        return "Add"
    new_user_dict = {"username":username, "password":password, "user_role":user_role, "email":email, "project_id":project['project_id']}
    user_op.create_user(new_user_dict)
    return "ProjUsers"


def userDel(d, user_op, user):
    yesno = d.yesno("Are you sure you would like to delete this User?",
         yes_label="Yes, I'm sooo sure",
         no_label="No, not yet", width=80)
    
    if(yesno == d.DIALOG_OK):
        delete_dict = {"username":user['username'], "user_id":user['user_id']}
        user_op.delete_user(delete_dict)


def userInfo(d, user):
    while True:
        (code, tag) = d.radiolist(
            user['username'] + " - User Options",
            width=65,
            choices=[("Manage", "Manage this user", 0),
                     ("Delete", "Completely remove this user", 0),
                     ("Back", "Return to users", 1)])
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag


def userManage(d, user_op, user):
    HIDDEN = 0x1
    while True:
        elements = [
            ("Name:", 1, 1, user['username'], 1, 32, 40, 40, 0x0),
            ("Password:", 2, 1, "", 2, 32, 40, 40, HIDDEN),
            ("Re-Enter Password:", 3, 1, "", 3, 32, 40, 40, HIDDEN),
            ("Role (admin/pu/user):", 4, 1, user['user_role'], 4, 32, 40, 40, 0x0),
            ("Email", 5, 1, user['email'], 5, 32, 40, 40, 0x0)]

        (code, fields) = d.mixedform(
            "Update User Info:", elements, insecure=True, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
        if handle_exit_code(d, code) == d.DIALOG_CANCEL:
            return
    username, password, confirm, user_role, email = fields
    if(password != ""):
        if(password != confirm):
            d.msgbox("Passwords did not match, try again.")
            return "Manage"
        else:
            update_pass_dict = {"new_password": password, "project_id": user['project_id'], "user_id": user['user_id']}
            user_op.update_user_password(update_pass_dict)
    if(user_role != "admin" and user_role != "pu" and user_role != "user"):
        d.msgbox("Role must be admin, pu or user, try again.")
        return "Manage"
    update_dict = {"username": user['username']}
    if(username != user['username']):
        update_dict['new_username'] = username
    if(user_role != user['user_role']):
        update_dict['new_role'] = user_role
    if(email != user['email']):
        update_dict['email'] = email
    user_op.update_user (update_dict)
    return "OK"


def projInstances(d, project):
    addChoice = ("Add", "Add an Instance", 0)
    projChoice = ("Back", "Return to Project Components", 1)
    allChoices = []
    counter = 0

    for entry in project['instances']:
        counter += 1
        choice = (str(counter), entry['name'], 0)
        allChoices.append(choice)
    allChoices.append(addChoice)
    allChoices.append(projChoice)
    while True:
        (code, tag) = d.radiolist(project['name'] + " - Select Instance to Manage",
        width=65, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag


def instanceAdd(d):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Flavor:", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("Image:", 3, 1, "", 3, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Add Instance:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def instanceDel(d, instance):
    return d.yesno("Are you sure you would like to delete this Instance?",
         yes_label="Yes, I'm sooo sure",
         no_label="No, not yet", width=80)

def instanceInfo(d, instance):
    while True:
        (code, tag) = d.radiolist(
            instance['name'] + " - Instance Options",
            width=65,
            choices=[("Manage", "Manage this instance", 0),
                     ("Delete", "Completely remove this instance", 0),
                     ("Back", "Return to instances", 1)])
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def instanceManage(d, instance):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Flavor:", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("Image:", 3, 1, "", 3, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Update Instance Info:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def projVolumes(d, project):
    addChoice = ("Add", "Add a Volume", 0)
    projChoice = ("Back", "Return to Project Components", 1)
    allChoices = []
    counter = 0

    for entry in project['volumes']:
        counter += 1
        choice = (str(counter), entry['name'], 0)
        allChoices.append(choice)
    allChoices.append(addChoice)
    allChoices.append(projChoice)
    while True:
        (code, tag) = d.radiolist(project['name'] + " - Select Volume to Manage",
        width=65, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def volumeAdd(d):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Size:", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("Attached:", 3, 1, "", 3, 24, 16, 16, 0x0),
            ("Instance:", 4, 1, "", 4, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Add Volume:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def volumeDel(d, volume):
    return d.yesno("Are you sure you would like to delete this Volume?",
         yes_label="Yes, I'm sooo sure",
         no_label="No, not yet", width=80)

def volumeInfo(d, volume):
    while True:
        (code, tag) = d.radiolist(
            volume['name'] + " - Volume Options",
            width=65,
            choices=[("Manage", "Manage this volume", 0),
                     ("Delete", "Completely remove this volume", 0),
                     ("Back", "Return to volumes", 1)])
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def volumeManage(d, volume):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Size:", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("Attached:", 3, 1, "", 3, 24, 16, 16, 0x0),
            ("Instance:", 4, 1, "", 4, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Update Volume Info:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def projContainers(d, project):
    addChoice = ("Add", "Add a Container", 0)
    projChoice = ("Back", "Return to Project Components", 1)
    allChoices = []
    counter = 0

    for entry in project['containers']:
        counter += 1
        choice = (str(counter), entry['name'], 0)
        allChoices.append(choice)
    allChoices.append(addChoice)
    allChoices.append(projChoice)
    while True:
        (code, tag) = d.radiolist(project['name'] + " - Select Container to Manage",
        width=65, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def containerAdd(d):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Size:", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("Attached:", 3, 1, "", 3, 24, 16, 16, 0x0),
            ("Instance:", 4, 1, "", 4, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Add Container:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def containerDel(d, container):
    return d.yesno("Are you sure you would like to delete this Container?",
         yes_label="Yes, I'm sooo sure",
         no_label="No, not yet", width=80)

def containerInfo(d, container):
    while True:
        (code, tag) = d.radiolist(
            container['name'] + " - Container Options",
            width=65,
            choices=[("Manage", "Manage this container", 0),
                     ("Delete", "Completely remove this container", 0),
                     ("Back", "Return to containers", 1)])
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def containerManage(d, container):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Size:", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("Attached:", 3, 1, "", 3, 24, 16, 16, 0x0),
            ("Instance:", 4, 1, "", 4, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Update Container Info:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def projSnapshots(d, project):
    addChoice = ("Add", "Add a Snapshot", 0)
    projChoice = ("Back", "Return to Project Components", 1)
    allChoices = []
    counter = 0

    for entry in project['snapshots']:
        counter += 1
        choice = (str(counter), entry['name'], 0)
        allChoices.append(choice)
    allChoices.append(addChoice)
    allChoices.append(projChoice)
    while True:
        (code, tag) = d.radiolist(project['name'] + " - Select Snapshot to Manage",
        width=65, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def snapshotAdd(d):
    while True:
        elements = [
            ("Description:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Size:", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("Created at:", 3, 1, "", 3, 24, 16, 16, 0x0),
            ("Volume:", 4, 1, "", 4, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Add Snapshot:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def snapshotDel(d, snapshot):
    return d.yesno("Are you sure you would like to delete this Snapshot?",
         yes_label="Yes, I'm sooo sure",
         no_label="No, not yet", width=80)

def snapshotInfo(d, snapshot):
    while True:
        (code, tag) = d.radiolist(
            snapshot['name'] + " - Snapshot Options",
            width=65,
            choices=[("Manage", "Manage this snapshot", 0),
                     ("Delete", "Completely remove this snapshot", 0),
                     ("Back", "Return to snapshots", 1)])
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def snapshotManage(d, snapshot):
    while True:
        elements = [
            ("Description:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Size:", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("Created at:", 3, 1, "", 3, 24, 16, 16, 0x0),
            ("Volume:", 4, 1, "", 4, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Update Snapshot Info:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def projImages(d, project):
    addChoice = ("Add", "Add a Image", 0)
    projChoice = ("Back", "Return to Project Components", 1)
    allChoices = []
    counter = 0

    for entry in project['images']:
        counter += 1
        choice = (str(counter), entry['name'], 0)
        allChoices.append(choice)
    allChoices.append(addChoice)
    allChoices.append(projChoice)
    while True:
        (code, tag) = d.radiolist(project['name'] + " - Select Image to Manage",
        width=65, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def imageAdd(d):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Disk Format:", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("Container Format:", 3, 1, "", 3, 24, 16, 16, 0x0),
            ("Visibility:", 4, 1, "", 4, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Add Image:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def imageDel(d, image):
    return d.yesno("Are you sure you would like to delete this Image?",
         yes_label="Yes, I'm sooo sure",
         no_label="No, not yet", width=80)

def imageInfo(d, image):
    while True:
        (code, tag) = d.radiolist(
            image['name'] + " - Image Options",
            width=65,
            choices=[("Manage", "Manage this image", 0),
                     ("Delete", "Completely remove this image", 0),
                     ("Back", "Return to images", 1)])
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def imageManage(d, image):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Disk Format:", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("Container Format:", 3, 1, "", 3, 24, 16, 16, 0x0),
            ("Visibility:", 4, 1, "", 4, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Update Image Info:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def projSecurityGroups(d, project):
    addChoice = ("Add", "Add a Security Group", 0)
    projChoice = ("Back", "Return to Project Components", 1)
    allChoices = []
    counter = 0

    for entry in project['securityGroups']:
        counter += 1
        choice = (str(counter), entry['name'], 0)
        allChoices.append(choice)
    allChoices.append(addChoice)
    allChoices.append(projChoice)
    while True:
        (code, tag) = d.radiolist(project['name'] + " - Select Security Group to Manage",
        width=65, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def securityGroupAdd(d):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Protocol:", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("Port Min:", 3, 1, "", 3, 24, 16, 16, 0x0),
            ("Port Max:", 4, 1, "", 4, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Add Security Group:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def securityGroupDel(d, securitygroup):
    return d.yesno("Are you sure you would like to delete this Security Group?",
         yes_label="Yes, I'm sooo sure",
         no_label="No, not yet", width=80)

def securityGroupInfo(d, securitygroup):
    while True:
        (code, tag) = d.radiolist(
            securitygroup['name'] + " - Security Group Options",
            width=65,
            choices=[("Manage", "Manage this Security Group", 0),
                     ("Delete", "Completely remove this Security Group", 0),
                     ("Back", "Return to Security Groups", 1)])
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def securityGroupManage(d, securitygroup):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Protocol:", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("Port Min:", 3, 1, "", 3, 24, 16, 16, 0x0),
            ("Port Max:", 4, 1, "", 4, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Update Security Group Info:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def projKeypairs(d, project):
    addChoice = ("Add", "Add a Keypair", 0)
    projChoice = ("Back", "Return to Project Components", 1)
    allChoices = []
    counter = 0

    for entry in project['keypairs']:
        counter += 1
        choice = (str(counter), entry['name'], 0)
        allChoices.append(choice)
    allChoices.append(addChoice)
    allChoices.append(projChoice)
    while True:
        (code, tag) = d.radiolist(project['name'] + " - Select Keypair to Manage",
        width=65, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def keypairAdd(d):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("File Location:", 2, 1, "", 2, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Add Keypair:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def keypairDel(d, keypair):
    return d.yesno("Are you sure you would like to delete this Keypair?",
         yes_label="Yes, I'm sooo sure",
         no_label="No, not yet", width=80)

def keypairInfo(d, keypair):
    while True:
        (code, tag) = d.radiolist(
            keypair['name'] + " - Keypair Options",
            width=65,
            choices=[("Manage", "Manage this keypair", 0),
                     ("Delete", "Completely remove this keypair", 0),
                     ("Back", "Return to keypairs", 1)])
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def keypairManage(d, keypair):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("File Location:", 2, 1, "", 2, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Update Keypair Info:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields


def projNetworks(d, project):
    addChoice = ("Add", "Add a Network", 0)
    projChoice = ("Back", "Return to Project Components", 1)
    allChoices = []
    counter = 0

    for entry in project['networks']:
        counter += 1
        choice = (str(counter), entry['name'], 0)
        allChoices.append(choice)
    allChoices.append(addChoice)
    allChoices.append(projChoice)
    while True:
        (code, tag) = d.radiolist(project['name'] + " - Select Network to Manage",
        width=65, choices=allChoices)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def networkAdd(d):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Tunneling (true/false):", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("ID Min:", 3, 1, "", 3, 24, 16, 16, 0x0),
            ("ID Max:", 4, 1, "", 4, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Add Network:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def networkDel(d, network):
    return d.yesno("Are you sure you would like to delete this Network?",
         yes_label="Yes, I'm sooo sure",
         no_label="No, not yet", width=80)

def networkInfo(d, network):
    while True:
        (code, tag) = d.radiolist(
            network['name'] + " - Network Options",
            width=65,
            choices=[("Manage", "Manage this network", 0),
                     ("Delete", "Completely remove this network", 0),
                     ("Back", "Return to networks", 1)])
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return tag

def networkManage(d, network):
    while True:
        elements = [
            ("Name:", 1, 1, "", 1, 24, 16, 16, 0x0),
            ("Tunneling (true/false):", 2, 1, "", 2, 24, 16, 16, 0x0),
            ("ID Min:", 3, 1, "", 3, 24, 16, 16, 0x0),
            ("ID Max:", 4, 1, "", 4, 24, 16, 16, 0x0)]

        (code, fields) = d.mixedform(
            "Update Network Info:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields

def dash(d, auth_dict):
    tenant_op = tenant_ops(auth_dict)
    user_op = user_ops(auth_dict)
    
    nodeList = node_op.list_nodes()
    
    userList = [{'name':"Snow White",
                 'role':"User",
                 'status':2,
                 'isAdmin':False},
                {'name':"Pocahontas",
                 'role':"PowerUser",
                 'status':1,
                 'isAdmin':False},
                {'name':"Rapunzel",
                 'role':"PowerUser",
                 'status':1,
                 'isAdmin':False},
                {'name':"Tiana",
                 'role':"PowerUser",
                 'status':1,
                 'isAdmin':False}]

    while True:
        selection = dashboard(d)
        while(selection == "Nodes"):

#/============================Nodes Start=========================

            selection = nodes(d, nodeList)
            if(selection == "Dashboard"):
                continue

#/----------------------------Node Remove Start--------------------------

            elif(selection == "Remove"):
                while(selection == "Remove"):
                    selection = nodeRemove(d, nodeList)
                    if(selection == "Back"):
                        selection = "Nodes"
                        continue
                    elif(int(selection) >= 1 and int(selection) <= len(nodeList)):
                        node = nodeList[int(selection) - 1]
                        nodeDel(d, node)
                        selection = "Nodes"
                        continue

#----------------------------Node Remove End--------------------------/

            elif(int(selection) >= 1 and int(selection) <= len(nodeList)):
                node = nodeList[int(selection) - 1]
                selection = "NodeInfo"
                while(selection == "NodeInfo"):

#/----------------------------Node Info Start-------------------------

                    selection = nodeInfo(d, node)
                    if(selection == d.DIALOG_OK):
                        selection = "NodeManage"
                        while(selection == "NodeManage"):

#/----------------------------Node Manage Start--------------------------

                            nodeManage(d, node)
                            selection = "NodeInfo"
                            continue

#----------------------------Node Manage End--------------------------/

                    elif(selection == d.DIALOG_CANCEL):
                        selection = "Nodes"
                        continue

#----------------------------Node Info End--------------------------/

#============================Nodes End=========================/

        while(selection == "Projects"):

#/============================Projects Start=========================
            projectList = tenant_op.list_all_tenants()
            selection = projects(d, projectList)
            if(selection == "Add"):
                while(selection == "Add"):
                    selection = projectAdd(d, auth_dict)
            elif(selection == "Dashboard"):
                continue
            elif(int(selection) >= 1 and int(selection) <= len(projectList)):
                project = projectList[int(selection) - 1]
                selection = "ProjInfo"
                while(selection == "ProjInfo"):

#/----------------------------Project Info Start-------------------------

                    selection = projectInfo(d, project)
                    if(selection == d.DIALOG_OK):
                        selection = "ProjManage"
                        while(selection == "ProjManage"):

#/----------------------------Project Manage Start--------------------------

                            selection = projectManage(d, project)
                            if(selection == "Users"):
                                selection = "ProjUsers"
                                while(selection == "ProjUsers"):

#/----------------------------Project Users Start-------------------------
                                    userList = tenant_op.list_tenant_users(project['project_id'])
                                    selection = projUsers(d, tenant_op, project)
                                    if(selection == "Add"):
                                        while(selection == "Add"):
                                            selection = userAdd(d, user_op, project)
                                    elif(selection == "Back"):
                                        selection = "ProjManage"
                                        continue
                                    elif(int(selection) >= 1 and int(selection) <= len(userList)):
                                        user = userList[int(selection) - 1]
                                        user_info_dict = {"username": user['username'], "project_name": project['project_name']}
                                        user = user_op.get_user_info(user_info_dict)
                                        selection = "UserManage"
                                        while(selection == "UserManage"):
                                            selection = userInfo(d, user)
                                            if(selection == "Manage"):
                                                while(selection == "Manage"):
                                                    selection = userManage(d, user_op, user)
                                                selection = "UserManage"
                                            elif(selection == "Delete"):
                                                userDel(d, user_op, user)
                                                selection = "ProjUsers"
                                                continue
                                            elif(selection == "Back"):
                                                selection = "ProjUsers"
                                                continue

#-----------------------------Project Users End-------------------------/

                            elif(selection == "Instances"):
                                selection = "ProjInstances"
                                while(selection == "ProjInstances"):

#/----------------------------Project Instances Start--------------------------

                                    selection = projInstances(d, project)
                                    if(selection == "Add"):
                                        instanceAdd(d)
                                        selection = "ProjInstances"
                                        continue
                                    elif(selection == "Back"):
                                        selection = "ProjManage"
                                        continue
                                    elif(int(selection) >= 1 and int(selection) <= len(project['instances'])):
                                        instance = project['instances'][int(selection) - 1]
                                        selection = "InstanceManage"
                                        while(selection == "InstanceManage"):
                                            selection = instanceInfo(d, instance)
                                            if(selection == "Manage"):
                                                selection = instanceManage(d, instance)
                                                selection = "InstanceManage"
                                            elif(selection == "Delete"):
                                                instanceDel(d, instance)
                                                selection = "ProjInstances"
                                                continue
                                            elif(selection == "Back"):
                                                selection = "ProjInstances"
                                                continue


#-----------------------------Project Instances End---------------------------/

                            elif(selection == "Volumes"):
                                selection = "ProjVolumes"
                                while(selection == "ProjVolumes"):

#/----------------------------Project Volumes Start--------------------------

                                    selection = projVolumes(d, project)
                                    if(selection == "Add"):
                                        volumeAdd(d)
                                        selection = "ProjVolumes"
                                        continue
                                    elif(selection == "Back"):
                                        selection = "ProjManage"
                                        continue
                                    elif(int(selection) >= 1 and int(selection) <= len(project['volumes'])):
                                        volume = project['volumes'][int(selection) - 1]
                                        selection = "VolumeManage"
                                        while(selection == "VolumeManage"):
                                            selection = volumeInfo(d, volume)
                                            if(selection == "Manage"):
                                                selection = volumeManage(d, volume)
                                                selection = "VolumeManage"
                                            elif(selection == "Delete"):
                                                volumeDel(d, volume)
                                                selection = "ProjVolumes"
                                                continue
                                            elif(selection == "Back"):
                                                selection = "ProjVolumes"
                                                continue


#-----------------------------Project Volumes End---------------------------/

                            elif(selection == "Containers"):
                                print "in containers"
                                selection = "ProjContainers"
                                while(selection == "ProjContainers"):

#/----------------------------Project Containers Start--------------------------

                                    selection = projContainers(d, project)
                                    if(selection == "Add"):
                                        containerAdd(d)
                                        selection = "ProjContainers"
                                        continue
                                    elif(selection == "Back"):
                                        selection = "ProjManage"
                                        continue
                                    elif(int(selection) >= 1 and int(selection) <= len(project['containers'])):
                                        container = project['containers'][int(selection) - 1]
                                        selection = "ContainerManage"
                                        while(selection == "ContainerManage"):
                                            selection = containerInfo(d, container)
                                            if(selection == "Manage"):
                                                selection = containerManage(d, container)
                                                selection = "ContainerManage"
                                            elif(selection == "Delete"):
                                                containerDel(d, container)
                                                selection = "ProjContainers"
                                                continue
                                            elif(selection == "Back"):
                                                selection = "ProjContainers"
                                                continue


#-----------------------------Project Containers End---------------------------/

                            elif(selection == "Snapshots"):
                                selection = "ProjSnapshots"
                                while(selection == "ProjSnapshots"):

#/----------------------------Project Snapshots Start--------------------------

                                    selection = projSnapshots(d, project)
                                    if(selection == "Add"):
                                        snapshotAdd(d)
                                        selection = "ProjSnapshots"
                                        continue
                                    elif(selection == "Back"):
                                        selection = "ProjManage"
                                        continue
                                    elif(int(selection) >= 1 and int(selection) <= len(project['snapshots'])):
                                        snapshot = project['snapshots'][int(selection) - 1]
                                        selection = "SnapshotManage"
                                        while(selection == "SnapshotManage"):
                                            selection = snapshotInfo(d, snapshot)
                                            if(selection == "Manage"):
                                                selection = snapshotManage(d, snapshot)
                                                selection = "SnapshotManage"
                                            elif(selection == "Delete"):
                                                snapshotDel(d, snapshot)
                                                selection = "ProjSnapshots"
                                                continue
                                            elif(selection == "Back"):
                                                selection = "ProjSnapshots"
                                                continue

#-----------------------------Project Snapshots End---------------------------/

                            elif(selection == "Images"):
                                selection = "ProjImages"
                                while(selection == "ProjImages"):

#/----------------------------Project Images Start--------------------------

                                    selection = projImages(d, project)
                                    if(selection == "Add"):
                                        imageAdd(d)
                                        selection = "ProjImages"
                                        continue
                                    elif(selection == "Back"):
                                        selection = "ProjManage"
                                        continue
                                    elif(int(selection) >= 1 and int(selection) <= len(project['images'])):
                                        image = project['images'][int(selection) - 1]
                                        selection = "ImageManage"
                                        while(selection == "ImageManage"):
                                            selection = imageInfo(d, image)
                                            if(selection == "Manage"):
                                                selection = imageManage(d, image)
                                                selection = "ImageManage"
                                            elif(selection == "Delete"):
                                                imageDel(d, image)
                                                selection = "ProjImages"
                                                continue
                                            elif(selection == "Back"):
                                                selection = "ProjImages"
                                                continue

#-----------------------------Project Images End---------------------------/

                            elif(selection == "Security Groups"):
                                selection = "ProjSecurityGroups"
                                while(selection == "ProjSecurityGroups"):

#/----------------------------Project Securitygroups Start--------------------------

                                    selection = projSecurityGroups(d, project)
                                    if(selection == "Add"):
                                        securitygroupAdd(d)
                                        selection = "ProjSecurityGroups"
                                        continue
                                    elif(selection == "Back"):
                                        selection = "ProjManage"
                                        continue
                                    elif(int(selection) >= 1 and int(selection) <= len(project['securityGroups'])):
                                        securitygroup = project['securitygroups'][int(selection) - 1]
                                        selection = "SecurityGroupManage"
                                        while(selection == "SecurityGroupManage"):
                                            selection = securitygroupInfo(d, securitygroup)
                                            if(selection == "Manage"):
                                                selection = securityGroupManage(d, securitygroup)
                                                selection = "SecurityGroupManage"
                                            elif(selection == "Delete"):
                                                securitygroupDel(d, securitygroup)
                                                selection = "ProjSecurityGroups"
                                                continue
                                            elif(selection == "Back"):
                                                selection = "ProjSecurityGroups"
                                                continue

#-----------------------------Project Security Groups End---------------------------/

                            elif(selection == "Keypairs"):
                                selection = "ProjKeypairs"
                                while(selection == "ProjKeypairs"):

#/----------------------------Project Keypairs Start--------------------------

                                    selection = projKeypairs(d, project)
                                    if(selection == "Add"):
                                        keypairAdd(d)
                                        selection = "ProjKeypairs"
                                        continue
                                    elif(selection == "Back"):
                                        selection = "ProjManage"
                                        continue
                                    elif(int(selection) >= 1 and int(selection) <= len(project['keypairs'])):
                                        keypair = project['keypairs'][int(selection) - 1]
                                        selection = "KeypairManage"
                                        while(selection == "KeypairManage"):
                                            selection = keypairInfo(d, keypair)
                                            if(selection == "Manage"):
                                                selection = keypairManage(d, keypair)
                                                selection = "KeypairManage"
                                            elif(selection == "Delete"):
                                                keypairDel(d, keypair)
                                                selection = "ProjKeypairs"
                                                continue
                                            elif(selection == "Back"):
                                                selection = "ProjKeypairs"
                                                continue

#-----------------------------Project Keypairs End---------------------------/

                            elif(selection == "Networks"):
                                selection = "ProjNetworks"
                                while(selection == "ProjNetworks"):

#/----------------------------Project Networks Start--------------------------

                                    selection = projNetworks(d, project)
                                    if(selection == "Add"):
                                        networkAdd(d)
                                        selection = "ProjNetworks"
                                        continue
                                    elif(selection == "Back"):
                                        selection = "ProjManage"
                                        continue
                                    elif(int(selection) >= 1 and int(selection) <= len(project['networks'])):
                                        network = project['networks'][int(selection) - 1]
                                        selection = "NetworkManage"
                                        while(selection == "NetworkManage"):
                                            selection = networkInfo(d, network)
                                            if(selection == "Manage"):
                                                selection = networkManage(d, network)
                                                selection = "NetworkManage"
                                            elif(selection == "Delete"):
                                                networkDel(d, network)
                                                selection = "ProjNetworks"
                                                continue
                                            elif(selection == "Back"):
                                                selection = "ProjNetworks"
                                                continue

#-----------------------------Project Network End---------------------------/

#/----------------------------Project Delete Start--------------------------

                            elif(selection == "Delete"):
                                selection = projectDel(d, auth_dict, project)
                                continue

#-----------------------------Project Delete End---------------------------/

                            elif(selection == "Back"):
                                selection = "Projects"
                                continue

#-----------------------------Project Manage End---------------------------/

#-----------------------------Project Info End--------------------------------/

                if(selection == d.DIALOG_CANCEL):
                    selection = "Projects"

#=============================Projects End========================/

        while(selection == "Users"):

#/============================Users Start=========================

            selection = users(d, userList)
            if(selection == "Dashboard"):
                continue

            elif(selection == "Add"):
                while(selection == "Add"):
                    
#/----------------------------User Add Start--------------------------

                    userAdd(d)
                    selection = "Users"
                    continue

#----------------------------User Add End--------------------------/

            elif(int(selection) >= 1 and int(selection) <= len(userList)):
                user = userList[int(selection) - 1]
                selection = "UserInfo"
                while(selection == "UserInfo"):

#/----------------------------User Info Start-------------------------

                    selection = userInfo(d, user)
                    if(selection == "Manage"):
                        selection = userManage(d, user)
                        selection = "Users"
                    elif(selection == "Delete"):
                        userDel(d, user)
                        selection = "Users"
                        continue
                    elif(selection == "Back"):
                        selection = "Users"
                        continue

#----------------------------User Info End--------------------------/



#============================Users End=========================/

    clear_screen(d)


def clear_screen(d):
    program = "clear"

    try:
        p = subprocess.Popen([program], shell=False, stdout=None, stderr=None,
                             close_fds=True)
        retcode = p.wait()
    except os.error, e:
        d.msgbox("Unable to execute program '%s': %s." % (program,
                                                          e.strerror),
                 title="Error")
        return -1

    if retcode > 0:
        msg = "Program %s returned exit code %u." % (program, retcode)
    elif retcode < 0:
        msg = "Program %s was terminated by signal %u." % (program, -retcode)
    else:
        return 0

    d.msgbox(msg)
    return -1


def process_command_line():
    global params

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ft",
                                   ["test-suite",
                                    "fast",
                                    "help",
                                    "version"])
    except getopt.GetoptError, message:
        sys.stderr.write(usage + "\n")
        return ("exit", 1)

    # Let's start with the options that don't require any non-option argument
    # to be present
    for option, value in opts:
        if option == "--help":
            print usage
            return ("exit", 0)
        elif option == "--version":
            print "%s %s\n%s" % (progname, progversion, version_blurb)
            return ("exit", 0)

    # Now, require a correct invocation.
    if len(args) != 0:
        sys.stderr.write(usage + "\n")
        return ("exit", 1)

    # Default values for parameters
    params = {"fast_mode": False,
              "testsuite_mode": False}

    # Get the home directory, if any, and store it in params (often useful).
    root_dir = os.sep           # This is OK for Unix-like systems
    params["home_dir"] = os.getenv("HOME", root_dir)

    # General option processing
    for option, value in opts:
        if option in ("-t", "--test-suite"):
            params["testsuite_mode"] = True
            # --test-suite implies --fast
            params["fast_mode"] = True
        elif option in ("-f", "--fast"):
            params["fast_mode"] = True
        else:
            # The options (such as --help) that cause immediate exit
            # were already checked, and caused the function to return.
            # Therefore, if we are here, it can't be due to any of these
            # options.
            assert False, "Unexpected option received from the " \
                "getopt module: '%s'" % option

    return ("continue", None)


def main(auth_dict):
    what_to_do, code = process_command_line()
    if what_to_do == "exit":
        sys.exit(code)

    try:
        # If you want to use Xdialog (pathnames are also OK for the 'dialog'
        # argument), you can use:
        #   d = dialog.Dialog(dialog="Xdialog", compat="Xdialog")
        d = dialog.Dialog(dialog="dialog")
        d.add_persistent_args(["--backtitle", "TransCirrus - CoalesceShell"])
        

        # Show the additional widgets before the "normal demo", so that I can
        # test new widgets quickly and simply hit Ctrl-C once they've been
        # shown.

        dash(d, auth_dict)
    except dialog.error, exc_instance:
        sys.stderr.write("Error:\n\n%s\n" % exc_instance.complete_message())
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__": main()

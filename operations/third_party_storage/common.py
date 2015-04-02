#
# Generic functions used by all 3rd party configs
#   These functions are PRIVATE and should not be called
#   directly from outside of the 3rd party functions.
#

import os
import subprocess
from transcirrus.component.cinder.cinder_volume import volume_ops

# Common constants
CINDER_CONF = "/etc/cinder/cinder.conf"
#CINDER_CONF = "cinder.conf"


def backend_configured (backend_name):
    curr_file = CINDER_CONF
    infile = open (curr_file, 'rU')

    row = infile.readlines()

    for line in row:
        if line.find("enabled_backends") > -1:
            if line.find(backend_name) == -1:
                enabled = False
            else:
                enabled = True
            break

    infile.close()
    return (enabled)


def add_backend (backend_name):
    curr_file = CINDER_CONF
    new_file = curr_file + ".new"
    prev_file = curr_file + ".prev"

    infile = open (curr_file, 'rU')
    outfile = open (new_file, 'w')

    row = infile.readlines()
    updated = False

    for line in row:
        if line.find("enabled_backends") > -1:
            if line.find(backend_name) == -1:
                updated = True
                line = add_param (line, backend_name) + "\n"
            else:
                break
        outfile.writelines (line)

    infile.close()
    outfile.close()

    if updated:
        os.rename (curr_file, prev_file)
        os.rename (new_file, curr_file)
    else:
        os.remove (new_file)

    return (updated)


def delete_backend (backend_name):
    curr_file = CINDER_CONF
    new_file = curr_file + ".new"
    prev_file = curr_file + ".prev"

    infile = open (curr_file, 'rU')
    outfile = open (new_file, 'w')

    row = infile.readlines()
    updated = False

    for line in row:
        if line.find("enabled_backends") > -1:
            if line.find(backend_name) > -1:
                updated = True
                line = delete_param (line, backend_name) + "\n"
            else:
                break
        outfile.writelines (line)

    infile.close()
    outfile.close()

    if updated:
        os.rename (curr_file, prev_file)
        os.rename (new_file, curr_file)
    else:
        os.remove (new_file)

    return (updated)


def delete_stanza (stanza_name):
    curr_file = CINDER_CONF
    new_file = curr_file + ".new"
    prev_file = curr_file + ".prev"

    infile = open (curr_file, 'rU')
    outfile = open (new_file, 'w')

    row = infile.readlines()

    found_stanza = False
    print_stanza = True
    for line in row:
        if line.find("[" + stanza_name + "]") > -1:
            print_stanza = False
            found_stanza = True
            continue

        if line[0] == "[":
            print_stanza = True

        if print_stanza:
            outfile.writelines (line)

    infile.close()
    outfile.close()

    if found_stanza:
        os.rename (curr_file, prev_file)
        os.rename (new_file, curr_file)
    else:
        os.remove (new_file)

    return (found_stanza)


def add_param (line, param):
    mod_line = line.replace("\n", "")
    mod_line = mod_line.replace(" ", "")
    parts = mod_line.split("=")
 
    params = parts[1].split(",")
    params.append(param)

    new_line = parts[0] + "="
    for item in params:
        if item == "":
            continue
        new_line = new_line + item + ","
    if new_line[-1] == ",":
        new_line = new_line[:-1]

    return (new_line)


def get_params (line):
    mod_line = line.replace("\n", "")
    mod_line = mod_line.replace(" ", "")
    parts = mod_line.split("=")
 
    params = parts[1].split(",")
    return (params)


def delete_param (line, param):
    mod_line = line.replace("\n", "")
    mod_line = mod_line.replace(" ", "")
    parts = mod_line.split("=")
 
    params = parts[1].split(",")
    try:
        params.remove(param)
    except:
        return (mod_line)

    new_line = parts[0] + "="
    for item in params:
        if item == "":
            continue
        new_line = new_line + item + ","
    if new_line[-1] == ",":
        new_line = new_line[:-1]

    return (new_line)


def add_voltype (auth, name):
    vo = volume_ops(auth)
    vo.create_volume_type (name)
    return


def delete_voltype (auth, name):
    vo = volume_ops(auth)
    vo.delete_volume_type (name)
    return


def restart_cinder_volume_proc():
    subprocess.call ("service openstack-cinder-volume restart", shell=True)
    return

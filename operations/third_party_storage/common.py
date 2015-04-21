#
# Generic functions used by all 3rd party configs
#   These functions are PRIVATE and should not be called
#   directly from outside of the 3rd party functions.
#

import os
import subprocess
from transcirrus.component.cinder.cinder_volume import volume_ops
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
import json

# Common constants
CINDER_CONF = "/etc/cinder/cinder.conf"

# License key constants
STORAGE_KEY_LEN = 15
STORAGE_KEY_CUSTNUM_START = 0
STORAGE_KEY_CUSTNUM_END = STORAGE_KEY_CUSTNUM_START + 4
STORAGE_KEY_DATE_START = STORAGE_KEY_CUSTNUM_END
STORAGE_KEY_DATE_END = STORAGE_KEY_DATE_START + 5
STORAGE_KEY_CAPACITY_START = STORAGE_KEY_DATE_END
STORAGE_KEY_CAPACITY_END = STORAGE_KEY_CAPACITY_START + 3
STORAGE_KEY_VENDOR_START = STORAGE_KEY_CAPACITY_END
STORAGE_KEY_VENDOR_END = STORAGE_KEY_VENDOR_START + 1
STORAGE_KEY_CHKSUM_START = STORAGE_KEY_VENDOR_END
STORAGE_KEY_CHKSUM_END = STORAGE_KEY_CHKSUM_START + 2

def decode_license_key (key):
    key_valid = False
    cust_num = None
    date = None
    capacity = None
    vendor = None

    if len(key) == STORAGE_KEY_LEN:
        cust_num = int (key[STORAGE_KEY_CUSTNUM_START:STORAGE_KEY_CUSTNUM_END], 16)
        date     = int (key[STORAGE_KEY_DATE_START:STORAGE_KEY_DATE_END], 16)
        capacity = int (key[STORAGE_KEY_CAPACITY_START:STORAGE_KEY_CAPACITY_END], 16)
        vendor = int (key[STORAGE_KEY_VENDOR_START:STORAGE_KEY_VENDOR_END], 16)
        checksum = int (key[STORAGE_KEY_CHKSUM_START:STORAGE_KEY_CHKSUM_END], 16)

        subkey = str(cust_num) + str(date) + str(capacity) + str(vendor)
        chksum = 0
        for c in subkey:
            chksum = chksum + int(c, 16)
        if checksum == chksum:
            key_valid = True

    return (key_valid, cust_num, date, capacity, vendor)


def is_licensed (backend_name):
    try:
        handle = pgsql (config.TRANSCIRRUS_DB, config.TRAN_DB_PORT, config.TRAN_DB_NAME, config.TRAN_DB_USER, config.TRAN_DB_PASS)
    except Exception as e:
        raise Exception ("Could not connect to TransCirrus DB with error: %s" % e)

    try:
        license_key_name = backend_name + "_license"
        select_license = {'select':'param_value', 'from':'trans_system_settings', 'where':"parameter='%s'" % (license_key_name)}
        license = handle.pg_select (select_license)
    except Exception as e:
        raise Exception ("Could not get license key from TransCirrus DB with error: %s" % e)
    finally:
        handle.pg_close_connection()

    if len(license) == 0:
        return (False)

    return (True)


def add_license (backend_name, key):
    if is_licensed (backend_name):
        return (True)

    try:
        handle = pgsql (config.TRANSCIRRUS_DB, config.TRAN_DB_PORT, config.TRAN_DB_NAME, config.TRAN_DB_USER, config.TRAN_DB_PASS)
    except Exception as e:
        raise Exception ("Could not connect to TransCirrus DB with error: %s" % e)

    key_valid, cust_num, date, capacity, vendor = decode_license_key (key)
    if not key_valid:
        return (False)

    lic_data = '{"key": "%s", "cust_num": "%s", "date": "%06d", "capacity": "%s", "vendor": "%s"}' % (key, cust_num, date, capacity, vendor)
    license_key_name = backend_name + "_license"

    try:
        insert_lic = {"parameter": license_key_name, "param_value": lic_data}
        handle.pg_insert ("trans_system_settings", insert_lic)
    except Exception, e:
        raise Exception ("Error adding license key into TransCirrus DB: %s" % e)
    finally:
        handle.pg_close_connection()

    return (True)


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
    vol_type = vo.create_volume_type (name)

    type_dict = {}
    type_dict['volume_type_id'] = vol_type['volume_type_id']
    type_dict['volume_backend_name'] = vol_type['volume_type_name']

    vo.assign_volume_type_to_backend (type_dict)
    return


def delete_voltype (auth, name):
    vo = volume_ops(auth)
    vo.delete_volume_type (name)
    return


def restart_cinder_volume_proc():
    subprocess.call ("service openstack-cinder-volume restart", shell=True)
    return

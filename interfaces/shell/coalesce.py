# -*- coding: utf-8 -*-
#!/usr/bin/env python


"""Setup for Transcirrus CiaC"""

from __future__ import nested_scopes, division
import sys, os, time, getopt, subprocess, dialog
from transcirrus.common.auth import authorization
from transcirrus.common import node_util
from transcirrus.common import util
from transcirrus.operations.initial_setup import run_setup

progname = os.path.basename(sys.argv[0])
progversion = "0.3"
version_blurb = """Setup for Transcirrus CiaC
                   Version 0.1 2013"""

usage = """Usage: %(progname)s [option ...]
Setup for Transcirrus CiaC.

Options:
      --help                   display this message and exit
      --version                output version information and exit""" \
  % { "progname": progname }

# Global parameters
params = {}


def handle_exit_code(d, code):
    """Function showing how to interpret the dialog exit codes.

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
                  "exit setup?"
        else:
            msg = "You pressed ESC in the last dialog box. Do you want to " \
                  "exit setup?"
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


def controls(d):
    """Defines the UI controls for the user"""
    d.msgbox("Use SPACE to select items (ie in a radio list) "
              "Use ARROW KEYS to move the cursor \n"
              "Use ENTER to submit and advance (OK or Cancel)", width=50)


def userbox(d):
    """Takes input of username"""
    while True:
        (code, answer) = d.inputbox("Username:", init="")
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return answer


def passwordbox(d):
    """Takes input of password"""
    while True:
        # 'insecure' keyword argument only asks dialog to echo asterisks when
        # the user types characters. Not *that* bad.
        (code, password) = d.passwordbox("Password:", insecure=True)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return password


def firstTimeFlag(d):
    # Return the answer given to the question (also specifies if ESC was
    # pressed)
    return d.yesno("Would you like to perform Setup?",
         yes_label="Yes, take me to Setup",
         no_label="No, take me to Coalesce Dashboard", width=80)


def info(d):
    while True:
        HIDDEN = 0x1
        elements = [
            ("Uplink IP:", 1, 1, "0.0.0.0", 1, 24, 40, 40, 0x0),
            ("Uplink Subnet Mask:", 2, 1, "0.0.0.0", 2, 24, 40, 40, 0x0),
            ("Uplink Gateway:", 3, 1, "0.0.0.0", 3, 24, 40, 40, 0x0),
            ("Uplink DNS:", 4, 1, "0.0.0.0", 4, 24, 40, 40, 0x0),
            ("Uplink Domain Name:", 5, 1, "0.0.0.0", 5, 24, 40, 40, 0x0),
            ("Management IP:", 6, 1, "0.0.0.0", 6, 24, 40, 40, 0x0),
            ("Management Subnet Mask:", 7, 1, "0.0.0.0", 7, 24, 40, 40, 0x0),
            ("Management DNS:", 8, 1, "0.0.0.0", 8, 24, 40, 40, 0x0),
            ("Management Domain Name:", 9, 1, "0.0.0.0", 9, 24, 40, 40, 0x0),
            ("VM Range Start-Point:", 10, 1, "0.0.0.0", 10, 24, 40, 40, 0x0),
            ("VM Range End-Point:", 11, 1, "0.0.0.0", 11, 24, 40, 40, 0x0),
            ("New Admin password:", 12, 1, "", 12, 24, 40, 40, HIDDEN),
            ("Confirm Password:", 13, 1, "", 13, 24, 40, 40, HIDDEN)]

        (code, fields) = d.mixedform(
            "Please fill in Cloud Information:", elements, width=77)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    return fields


def singleNode(d):
    # Return the answer given to the question (also specifies if ESC was
    # pressed)
    return d.yesno("Is this currently a single node system?",
         yes_label="Yes",
         no_label="No, it contains other nodes (enable DHCP)", width=100)


def dhcp(d):
    d.gauge_start("Progress: 0%", title="Enabling DHCP...")

    for i in range(1, 101):
        if i < 50:
            d.gauge_update(i, "Progress: %d%%" % i, update_text=1)
        elif i == 50:
            d.gauge_update(i, "Over %d%%. Good." % i, update_text=1)
        elif i == 80:
            d.gauge_update(i, "Yeah, this boring crap will be over Really "
                           "Soon Now.", update_text=1)
        else:
            d.gauge_update(i)

        time.sleep(0.01 if params["fast_mode"] else 0.1)

    d.gauge_stop()


def success(d, seconds):
    d.pause("""\
Setup has completed successfully.  The system will now restart in %u seconds\
 and update with the information you have entered.  To connect to this unit\
 again, use the newly created IP address and login credentials."""
% seconds, height=15, seconds=seconds)


def rollback(d, seconds):
    d.pause("""\
Setup has encountered an issue.  The system will now rollback in %u seconds\
 to factory defaults.  Attempt to rerun setup."""
% seconds, height=15, seconds=seconds)


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


def setup(d):
    d.msgbox("Hello, and welcome to CoalesceShell, the command-line " +
        "interface tool for your TransCirrus system.", width=60, height=10)
    controls(d)
    while(True):
        user = userbox(d)
        password = passwordbox(d)
        try:
            a = authorization(user, password)
            user_dict = a.get_auth()

            # Verify credentials
            # if cloud admin, continue setup
            # else re-prompt for credentials
            if (user_dict['is_admin'] == 1):
                break
            else:
                d.msgbox("Admin only, try again.", width=60, height=10)
        except:
            d.msgbox("Invalid credentials, try again.", width=60, height=10)

    first_time = node_util.check_first_time_boot()
    # Check to determine if first time (will be implemented differently
    # once we have those flags setup on database, this is just proof of concept
    if (first_time is False):
        d.msgbox("Taking you to the Coalesce Dashboard...")
        # Direct user to Coalesce Dashboard
        clear_screen(d)
        return
    else:
        d.msgbox("Continue to first time setup.")

    while(True):
        uplink_ip, uplink_subnet, uplink_gateway, uplink_dns, uplink_domain, 
        mgmt_ip, mgmt_subnet, mgmt_dns, mgmt_domain, 
        vm_ip_min, vm_ip_max, pwd, cnfrm, = info(d)
        # Validate uplink ip
        if(valid_ip(uplink_ip) is False):
            d.msgbox("Invalid Uplink IP, try again.", width=60, height=10)
            continue
        # Validate uplink subnet
        if(valid_ip(uplink_subnet) is False):
            d.msgbox("Invalid Uplink Subnet, try again.", width=60, height=10)
            continue
        # Validate uplink gateway
        if(valid_ip(uplink_gateway) is False):
            d.msgbox("Invalid Uplink Gateway, try again.", width=60, height=10)
            continue
        # Validate uplink dns
        if(valid_ip(uplink_dns) is False):
            d.msgbox("Invalid Uplink DNS, try again.", width=60, height=10)
            continue
        # Validate uplink domain
        if(valid_ip(uplink_domain) is False):
            d.msgbox("Invalid Uplink Domain, try again.", width=60, height=10)
            continue
        # Validate mgmt ip
        if(valid_ip(mgmt_ip) is False):
            d.msgbox("Invalid Management IP, try again.", width=60, height=10)
            continue
        # Validate mgmt subnet
        if(valid_ip(mgmt_subnet) is False):
            d.msgbox("Invalid Management Subnet, try again.", width=60, height=10)
            continue
        # Validate mgmt dns
        if(valid_ip(mgmt_dns) is False):
            d.msgbox("Invalid Management DNS, try again.", width=60, height=10)
            continue
        # Validate mgmt domain
        if(valid_ip(mgmt_domain) is False):
            d.msgbox("Invalid Management Domain, try again.", width=60, height=10)
            continue
        # Validate start point
        if(valid_ip_within(uplink_ip, vm_ip_min) is False):
            d.msgbox("Invalid VM Range Start-Point, try again.", width=60, height=10)
            continue
        # Validate end point
        if(valid_ip_within(vm_ip_min, vm_ip_max) is False):
            d.msgbox("Invalid VM Range End-Point, try again.", width=60, height=10)
            continue
        # Validate new password
        if(pwd != cnfrm and len(pwd) != 0 and len(cnfrm) != 0):
            d.msgbox("Passwords did not match, try again.", width=60, height=10)
            continue
        # Make sure uplink and mgmt IPs don't match
        if(uplink_ip == mgmt_ip):
            d.msgbox("Uplink IP and Management IP cannot match, try again.", width=60, height=10)
            continue
        break

    try:
        system = util.get_cloud_controller_name()
        new_system_variables = [
            {"system_name":system,"parameter":"api_ip","param_value": uplink_ip},
            {"system_name":system,"parameter":"mgmt_ip","param_value": mgmt_ip},
            {"system_name":system,"parameter":"admin_api_ip","param_value": uplink_ip},
            {"system_name":system,"parameter":"int_api_ip","param_value": uplink_ip},
            {"system_name":system,"parameter":"uplink_ip","param_value": uplink_ip},
            {"system_name":system,"parameter":"uplink_dns","param_value": uplink_dns},
            {"system_name":system,"parameter":"uplink_gateway","param_value": uplink_gateway},
            {"system_name":system,"parameter":"uplink_domain_name","param_value": uplink_domain},
            {"system_name":system,"parameter":"uplink_subnet","param_value": uplink_subnet},
            {"system_name":system,"parameter":"mgmt_domain_name","param_value": mgmt_domain},
            {"system_name":system,"parameter":"mgmt_subnet","param_value": mgmt_subnet},
            {"system_name":system,"parameter":"mgmt_dns","param_value": mgmt_dns},
            {"system_name":system,"parameter":"vm_ip_min","param_value": vm_ip_min},
            {"system_name":system,"parameter":"vm_ip_max","param_value": vm_ip_max}]

        ran = run_setup(new_system_variables)
        timeout = 20

        if(ran == "OK"):
            success(d, timeout)

        else:
            rollback(d, timeout)

    except Exception as e:
        d.msgbox("Error when updating database: " + str(e))

    node = util.get_node_id()
    system_variables = util.get_system_variables(node)
    sys_api_ip = system_variables['api_ip']
    sys_mgmt_ip = system_variables['mgmt_ip']
    sys_int_api_ip = system_variables['int_api_ip']
    sys_admin_api_ip = system_variables['admin_api_ip']
    sys_vm_ip_min = system_variables['vm_ip_min']
    sys_vm_ip_max = system_variables['vm_ip_max']
    sys_uplink_ip = system_variables['uplink_ip']

    d.msgbox("API_IP: " + sys_api_ip + "\n" +
             "MGMT_IP: " + sys_mgmt_ip + "\n" +
             "INT_API_IP: " + sys_int_api_ip + "\n" +
             "ADMIN_API_IP: " + sys_admin_api_ip + "\n" +
             "VM_IP_MIN: " + sys_vm_ip_min + "\n"
             "VM_IP_MAX: " + sys_vm_ip_max + "\n"
             "UPLINK IP: " + sys_uplink_ip + "\n", width=80, height=40)

    #single_node = singleNode(d)
    # Check to determine is system is single node
    # If not, enable DHCP
    #if (single_node == d.DIALOG_CANCEL):
        #dhcp(d)
        # Enable DHCP

    timeout = 20
    success(d, timeout)

    clear_screen(d)


def valid_ip(address):
    """
    Validate IP address's format:
        (only numbers and periods)
        (numbers between 0 and 255)
        (must have exactly 4 numbers)
        (must have exactly 3 periods)
        (must be the form #.#.#.#)
    """
    try:
        host_bytes = address.split('.')
        valid = [int(b) for b in host_bytes]
        valid = [b for b in valid if b >= 0 and b <= 255]
        return len(host_bytes) == 4 and len(valid) == 4
    except:
        return False


def valid_ip_within(broad, narrow):
    """
    Validate that the narrow IP address has the same network prefix of the broad IP address
    and that the host part of the narrow IP address is greater than or equal to that of the
    broad IP address
    """
    try:
        broad_bytes = broad.split('.')
        narrow_bytes = narrow.split('.')
        valid_broad = [int(b) for b in broad_bytes]
        valid_narrow = [int(b) for b in narrow_bytes]
        if (valid_broad[0] == valid_narrow[0] and
        valid_broad[1] == valid_narrow[1] and
        valid_broad[2] == valid_narrow[2] and
        valid_broad[3] <= valid_narrow[3]):
            return True
        else:
            return False
    except:
        return False


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


def main():
    what_to_do, code = process_command_line()
    if what_to_do == "exit":
        sys.exit(code)

    try:
        # If you want to use Xdialog (pathnames are also OK for the 'dialog'
        # argument), you can use:
        #   d = dialog.Dialog(dialog="Xdialog", compat="Xdialog")
        d = dialog.Dialog(dialog="dialog")
        d.add_persistent_args(["--backtitle", "TransCirrus - CoalesceShell"])

        setup(d)
    except dialog.error, exc_instance:
        sys.stderr.write("Error:\n\n%s\n" % exc_instance.complete_message())
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__": main()
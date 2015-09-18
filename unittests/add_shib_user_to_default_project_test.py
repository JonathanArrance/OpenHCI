# tpa_users_test

from transcirrus.operations.third_party_auth import tpa_users
from transcirrus.operations.third_party_auth import util as auth_util
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.component.keystone.keystone_tenants import tenant_ops
from transcirrus.common import extras as ex

protocols = auth_util.detect_auth()
if not protocols['has_shib']:
    print "shibboleth not added to cloud"
    exit

print "\nrunning 20 tpa_users tests\n==============================\n"

auth = ex.shadow_auth()

to = tenant_ops(auth)
uo = user_ops(auth)
default_project = to.get_default_tenant()

for x in range(20):
    test = "| test #%d |" %(x+1)
    bar_num = len(test)
    bars = "-" * bar_num
    print bars + "\n" + test + "\n" + bars + "\n"

    input_dict = {'username': 'myself', 'email': 'myself@testshib.org', 'project_id': default_project['project_id']}
    add_out = tpa_users.add_user(input_dict)

    added = "failure"
    if add_out is not None and add_out != "":
        added = "success"

    print "added:....." + added

    del_out = uo.delete_user(add_out)

    deleted = "failure"
    if del_out == "OK":
        deleted = "success"

    print "deleted:..." + deleted + "\n"

    passed = "***   FAILED   ***\n\n"
    if added == "success" and deleted == "success":
        passed = "***   PASSED   ***\n\n"

    print passed

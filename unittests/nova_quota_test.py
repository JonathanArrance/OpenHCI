#!/usr/bin/python
from transcirrus.common.auth import authorization
from transcirrus.component.nova.quota import quota_ops

print "Loggin in as the default admin."
a = authorization("admin","password")
d = a.get_auth()

print d
quota = quota_ops(d)
x = quota.get_project_quotas()
print x

print "project and user given"
input_dicty = {'user_id':'f7c4bfb8220f469d8112bae4ee8136e1', 'project_id':'54209ef0f7ba4935a2a8984cba4f27f2'}
y = quota.get_project_quotas('6492cba476994153800c5220a2f51bc2')
print y

print "user given"
input_dictz = {'user_id':'f7c4bfb8220f469d8112bae4ee8136e1'}
z = quota.show_user_quotas(input_dictz)
print z

print "project given"
input_dicta = {'project_id':'54209ef0f7ba4935a2a8984cba4f27f2'}
a = quota.show_user_quotas(input_dicta)
print a

input_dicty = {'user_id':'f7c4bfb8220f469d8112bae4ee8136e1', 'project_id':'8979d99d618045308817dcb2b8be068e'}
y = quota.get_project_quotas('8979d99d618045308817dcb2b8be068e')
print y

print "neither given"
b = quota.show_user_quotas()
print b

print "get max limits"
b = quota.get_max_limits("13d92fe4b2de4051abc5de0654277af0")
print b

input_dict = {'storage':'3000','instances':'20','cores':'25','snapshots':'30','volumes':'19','key_pairs':None,'ram':'90000','injected_file_content_bytes': None,'user_id':'f7c4bfb8220f469d8112bae4ee8136e1', 'project_id':'8979d99d618045308817dcb2b8be068e'}
f = quota.update_project_quotas(input_dict)
print f



#!/usr/bin/python
import sys
import time

import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.common.auth import authorization
from transcirrus.common.stats import stat_ops


print "**Instantiating Authorization Object for the Default Admin...**"
c = authorization("admin","password")
print

print "**Getting Admin Authorization Dictionary...**"
b = c.get_auth()
print

print "**Instantiating Stats Object...**"
s = stat_ops(b)
print s
print

print "**Getting Number of Projects...**"
num_proj = s.get_num_project()
print num_proj
print
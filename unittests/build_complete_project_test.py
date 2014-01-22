import sys
import time
import transcirrus.common.logger as logger
import transcirrus.common.config as config
from transcirrus.database.postgres import pgsql
from transcirrus.common.auth import authorization
from transcirrus.operations.build_complete_project import build_complete_project


a = authorization("admin","password")

#get the user dict
d = a.get_auth()
print d


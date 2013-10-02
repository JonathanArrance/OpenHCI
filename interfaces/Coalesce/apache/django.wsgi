# django.wsgi
import os, sys

os.environ['DJANGO_SETTINS_MODULE'] = 'FuelTool.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

path = 'C:\web'
if path not in sys.path
    sys.path.append(path)


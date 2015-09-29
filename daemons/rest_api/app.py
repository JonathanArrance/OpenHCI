from flask import Flask, jsonify
from flask import abort
from flask import make_response

import ast

from django.conf import settings
import transcirrus.interfaces.Coalesce.settings as tc_settings
settings.configure(default_settings=tc_settings, DEBUG=True, LOGGING_CONFIG=None, DATABASE_ROUTERS=[], USE_TZ=False, DEFAULT_INDEX_TABLESPACE="", CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',}},
                   DEFAULT_TABLESPACE="", USE_L10N=True, LOCALE_PATHS=(), FORMAT_MODULE_PATH=None, DEFAULT_CHARSET="utf-8", DEFAULT_CONTENT_TYPE="text/html")
from django.utils import simplejson

import sys
sys.path.append("/usr/local/lib/python2.7/transcirrus/interfaces/Coalesce/")

#from coalesce.coal_beta.forms import *
import transcirrus.interfaces.Coalesce.coalesce.coal_beta.views as views

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': {'message': "Not found", 'number': 404}}), 404)


@app.route("/tc/v1.0/version", methods=['GET'])
def get_version():
    request = ""
    ver_json = views.get_version(request)
    ver_dict = ast.literal_eval(ver_json.content)
    version = {'success': {}}
    version['success'] = {'release': ver_dict['data']['release'], 'major': ver_dict['data']['major'], 'full_str': ver_dict['data']['full_str'], 'short_str': ver_dict['data']['short_str'], 'minor': ver_dict['data']['minor']}
    print "version: %s" % version
    return jsonify({'version': version})
    #return (ver_json.content)


if __name__ == '__main__':
    app.run(host="192.168.10.46", port=6969, debug=True)

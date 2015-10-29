import json
import requests
import six.moves.urllib.parse as urlparse

class WebserviceClient(object):
    def __init__(self, scheme, host, port, service_path, **kwargs):
        self._validate_params(scheme, host, port)
        self._create_url(scheme, host, port, service_path)
        self._init_connection()
        return

    def _validate_params(self, scheme, host, port):
        if host is None or port is None or scheme is None:
            raise Exception ("One of the required inputs from host, port or scheme was not found.")
        if scheme not in ('http', 'https'):
            raise Exception ("Invalid transport type (%s)." % scheme)
        return

    def _create_url(self, scheme, host, port, service_path):
        netloc = '%s:%s' % (host, port)
        self.url = urlparse.urlunparse((scheme, netloc, service_path, None, None, None))
        return

    def _init_connection(self):
        self.conn = requests.Session()
        return

    def invoke_service(self, method='GET', url=None, params=None, data=None, headers=None, timeout=None, verify=False):
        if url == None:
            url = self.url
        try:
            response = self.conn.request(method, url, params, data, headers=headers, timeout=timeout, verify=verify)
        except Exception as e:
            raise Exception ("Error connecting to REST service: %s" % e)
        self._eval_response(response)
        return response

class RestClient(WebserviceClient):
    def __init__(self, scheme, host, port, service_path, **kwargs):
        super(RestClient, self).__init__(scheme, host, port, service_path, **kwargs)
        kwargs = kwargs or {}
        self.content_type = kwargs.get('content_type') or 'json'
        return

    def _get_resource_url(self, path, **kwargs):
        kwargs = kwargs or {}
        path = path.format(**kwargs)
        if not self.url.endswith('/'):
            self.url = '%s/' % self.url
        return urlparse.urljoin(self.url, path.lstrip('/'))

    def invoke(self, method, path, headers=None, data=None, timeout=None, verify=False, **kwargs):
        url = self._get_resource_url(path, **kwargs)
        if self.content_type == 'json':
                hdrs = {'Accept': 'application/json', 'Content-Type': 'application/json'}
                if headers != None:
                    hdrs.update(headers)
                data = json.dumps(data) if data else None
                res = self.invoke_service(method, url, data=data, headers=hdrs, timeout=timeout, verify=verify)
                return res.json() if res.text else None
        else:
            raise Exception ("Content type (%s) not supported." % self.content_type)
        return

    def _eval_response(self, response):
        status_code = int(response.status_code)
        if status_code >= 300:
            # Response code 422 returns error code and message
            if status_code == 422:
                msg = "Response code: %s - msg: %s." % (status_code, response.text)
            else:
                msg = "Response error code: %s." % status_code
            raise RestError(status_code, msg)
        return

class RestError(Exception):
    def __init__(self, error_code, message):
        super(RestError, self).__init__(message)
        self.error_code = error_code
        return

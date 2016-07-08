import json
import urllib2
import urllib

class HawkularAlertsError(urllib2.HTTPError):
    pass

class HawkularAlertsConnectionError(urllib2.URLError):
    pass

class HTTPErrorProcessor(urllib2.HTTPErrorProcessor):

    def http_response(self, request, response):
        if response.code < 300:
            return response
        return urllib2.HTTPErrorProcessor.http_response(self, request, response)

    https_response = http_response

class HawkularAlertsClient:
    """
    Creates a new client for Hawkular Alerting
    """
    def __init__(self,
                 user,
                 password,
                 tenant_id,
                 host='localhost',
                 port=8080,
                 path='hawkular/alerts'):

        self.user = user
        self.password = password
        self.tenant_id = tenant_id
        self.host = host
        self.port = port
        self.path = path

    """
    Internal methods
    """

    def _get_base_url(self):
        return "http://{0}:{1}/{2}/".format(self.host, str(self.port), self.path)

    def _get_status_url(self):
        return self._get_base_url() + 'status'

    def _http(self, url, method, data=None):
        res = None

        try:
            req = urllib2.Request(url=url)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Hawkular-Tenant', self.tenant_id)

            if not isinstance(data, str):
                data = json.dumps(data, indent=2)

            if data:
                req.add_data(data)

            req.get_method = lambda: method
            res = urllib2.urlopen(req)
            if method == 'GET':
                if res.getcode() == 200:
                    data = json.load(res)
                elif res.getcode() == 204:
                    data = {}

                return data

        except Exception as e:
            self._handle_error(e)

        finally:
            if res:
                res.close()

    def _get(self, url, **url_params):
        params = urllib.urlencode(url_params)
        if len(params) > 0:
            url = '{0}?{1}'.format(url, params)

        return self._http(url, 'GET')

    def _handle_error(self, e):
        if isinstance(e, urllib2.HTTPError):
            # Cast to HawkularAlertsError
            e.__class__ = HawkularAlertsError
            err_json = e.read()

            try:
                err_d = json.loads(err_json)
                e.msg = err_d['errorMsg']
            except:
                # Keep the original payload, couldn't parse it
                e.msg = err_json

            raise e
        elif isinstance(e, urllib2.URLError):
            # Cast to HawkularAlertsConnectionError
            e.__class__ = HawkularAlertsConnectionError
            e.msg = "Error, could not send event(s) to the Hawkular Alerts: " + str(e.reason)
            raise e
        else:
            raise e

    """
    External methods
    """

    """
    Instance methods
    """

    def status(self):
        return self._get(self._get_status_url())


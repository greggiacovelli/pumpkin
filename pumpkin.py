import datetime
import httplib
import json

import config

class Pumpkin:

    def __init__(self):
        self._connection = httplib.HTTPConnection(config.host, config.port, timeout=10)

    def deploy(self, environment, revision, api_key=None, deploy_time=None, host=None, build=None):
        if not api_key:
            api_key = config.default_api_key
        if not deploy_time:
            deploy_time = datetime.datetime.now()

        body = {
            'project': {'api_key': api_key},
            'environment': {'name': environment},
            'deploy': {'revision': revision,
                       'deployed_at': deploy_time.isoformat()
                      }
            
        }
        if build:
           body.deploy['build'] = build

        if host:
           body.deploy['hostname'] = host

        self._send('deploy', body)
        return 
        
    def _send(self, uri, body, method='POST'):
        self._connection.connect()
        self._connection.request(method, uri, json.dumps(body))
        response = self._connection.getresponse()
        status = response.status
        response_payload = response.read()
        if status is not 200:
            print response.reason, response_payload
        self._conection.close()
        return response, response_payload

if __name__() == 'main':
    a = Pumpkin()
    a.deploy('development', 'asdasdasdasd')


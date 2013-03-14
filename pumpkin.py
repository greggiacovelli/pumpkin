import datetime
import httplib
import json

from config import config


class ThreadBacktrace:

    backtraces = []

    def __init__(self, name, is_crash=False):
        self.name = name
        self.is_crash = is_crash

    def add_frame(self, file, line, symbol, type=None, **kwargs):
        frame = {
            'file': file,
            'line': line,
            'symbol': symbol
        }
        if type and kwargs:
            frame['type'] = type
            frame.update(kwargs)

        self.backtraces.append(frame)
    

class Pumpkin:

    VERSION = 'Pumpkin.py v1.0'

    def __init__(self):
        self._connection = httplib.HTTPConnection(config['host'], config['port'], timeout=10)
        self._connection.set_debuglevel(1)

    def deploy(self, environment, revision, api_key=None, deploy_time=None, host=None, build=None):
        if not api_key:
            api_key = config['default_api_key']
        if not deploy_time:
            deploy_time = datetime.datetime.now()
        if not build and not host:
            raise Exception('Need at least a Host or a build')

        body = {
            'project': {'api_key': api_key},
            'environment': {'name': environment},
            'deploy': {'revision': revision,
                       'deployed_at': deploy_time.isoformat()
                      }
            }
        if build:
           body['deploy']['build'] = build

        if host:
           body['deploy']['hostname'] = host

        self._send('/api/1.0/deploy', body)
        return 

    def notify(self, environment, backtraces, class_name, message, api_key=None, occurred_at=None, build=None, revision=None, **kwargs):
        if not api_key:
           api_key = config['default_api_key']
        if not occurred_at:
           occurred_at = datetime.datetime.now()
        if not build and not revision:
           raise Exception('Need at least a revision or a build')

        body = {
              'api_key': api_key,
              'environment': environment,
              'client': Pumpkin.VERSION,
              'class_name': class_name,
              'message': message,
              'occurred_at': occurred_at.isoformat()
             }

        traces = []
        for backtrace in backtraces:
            traces.append({
               'name': backtrace.name,
               'faulted': backtrace.is_crash,
               'backtrace': backtrace.backtraces
            })

        body['backtraces'] = traces

        if build:
           body['build'] = build

        if revision:
           body['revision'] = revision

        if kwargs:
           body.update(kwargs)
        self._send('/api/1.0/notify', body)
        
    def _send(self, uri, body, method='POST'):
        self._connection.connect()
        self._connection.request(method, uri, json.dumps(body), {'Content-Type': 'application/json'})
        response = self._connection.getresponse()
        status = response.status
        response_payload = response.read()
        print response.reason, response_payload
        self._connection.close()
        return response, response_payload

if __name__ == '__main__':
    print 'Making'
    a = Pumpkin()
    a.deploy('development', '03247c9ece2478b9abf5c46ad877326125569c6d', build='03247c9ece2478b9abf5c46ad877326125569c6d')
    backtrace = ThreadBacktrace('main', is_crash=True)
    backtrace.add_frame('File.java', 213, 'File')
    a.notify('development', [backtrace], 'NullPointerException', 'Nulls', build='03247c9ece2478b9abf5c46ad877326125569c6d', operating_system='Android')


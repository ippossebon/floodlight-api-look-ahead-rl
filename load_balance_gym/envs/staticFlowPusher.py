import http
import json

class StaticFlowPusher(object):

    def __init__(self, server):
        self.server = server

    def get(self, data):
        ret = self.rest_call({}, 'GET')
        return json.loads(ret[2])

    def set(self, data):
        ret = self.rest_call(data, 'POST')
        return ret[0] == 200

    # def remove(self, objtype, data):
    def remove(self, data):
        ret = self.rest_call(data, 'DELETE')
        return ret[0] == 200


    def rest_call(self, data, method):
        path = '/wm/staticflowpusher/json'
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            }
        body = json.dumps(data)

        conn = http.client.HTTPConnection(self.server, 8080)

        print('conn = ', conn)
        print('')
        print('method = ', method)
        print('path = ', path)
        print('body = ', body)
        print('headers = ', headers)

        conn.request(method, path, body, headers)

        response = conn.getresponse()
        ret = (response.status, response.reason, response.read())
        print(ret)
        conn.close()
        return(ret)

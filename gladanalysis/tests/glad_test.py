import unittest
import json
import logging
import requests
import os
import ast
from httmock import all_requests, response, HTTMock

from gladanalysis import create_application

@all_requests
def response_content(url, request):
    headers = {'content-type': 'application/json'}
    content = {'data': 'data'}
    return response(200, content, headers, None, 5, request)

class GladTest(unittest.TestCase):

    def setUp(self):
        app = create_application()
        app.testing = True
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def tearDown(self):
        pass

    def deserialize(self, response, status_code):
        if status_code == 200:
            resp_json = json.loads(response.text)
            return resp_json
            # return json.loads(response.data).get('data', None)
        elif status_code == 400:
            return json.loads(response.data).get('errors', None)

    def test_geostore_notfound(self):
        logging.info('[TEST]: Beginning Geostore NotFound Test')
        with HTTMock(response_content):
            response = self.app.get('/api/v2/ms/glad-alerts', follow_redirects=True)
            logging.info('[TEST]: response result: {}'.format(response))
            status_code = response.status_code
            data = self.deserialize(response, status_code)
            logging.info('[TEST]: response deserialized: {}'.format(data))
        self.assertEqual(status_code, 400)
        self.assertEqual(data[0].get('detail'), 'Geostore must be set')

    # def test_geostore(self):
    #     logging.info('[TEST]: Beginning Geostore Test')
    #     local_url = '{}'.format(os.getenv('LOCAL_URL'))
    #     with HTTMock(response_content):
    #         # response = self.app.get('{}/api/v2/ms/glad-alerts?geostore=beb8e2f26bd26406fcf2018d343a62c5'.format(local_url), follow_redirects=True)
    #         response = requests.get('{}/api/v2/ms/glad-alerts?geostore=beb8e2f26bd26406fcf2018d343a62c5'.format(local_url))
    #     logging.info('[TEST]: response result: {}'.format(response))
    #     status_code = response.status_code
    #     data = self.deserialize(response, status_code)
    #     logging.info('[TEST]: response deserialized: {}'.format(data))
    #     logging.info('[TEST]: response type: {}'.format(type(data)))
    #     self.assertEqual(status_code, 200)
    #     self.assertEqual(data['data']['geostore'], 'beb8e2f26bd26406fcf2018d343a62c5')

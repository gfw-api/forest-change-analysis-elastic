import unittest
import json
import logging
import requests
import os
from httmock import urlmatch, response, HTTMock

from gladanalysis import create_application

@urlmatch(path=r'.*/geostore.*')
def geostore_mock(url, request):
    headers = {'content-type': 'application/json'}
    content = {"data": {"attributes":{"areaHa":867570.6425005894,"downloadUrls":{"csv":"/download/f1dd79c3-e6d4-4d8c-b164-b4bd66f311ee?sql=SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day FROM index_f1dd79c3e6d44d8cb164b4bd66f311ee WHERE ((year = 2016 and julian_day >= 7) or (year = 2017 and julian_day <= 153))ORDER BY year, julian_day&format=csv&geostore=beb8e2f26bd26406fcf2018d343a62c5","json":"/download/f1dd79c3-e6d4-4d8c-b164-b4bd66f311ee?sql=SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day FROM index_f1dd79c3e6d44d8cb164b4bd66f311ee WHERE ((year = 2016 and julian_day >= 7) or (year = 2017 and julian_day <= 153))ORDER BY year, julian_day&format=json&geostore=beb8e2f26bd26406fcf2018d343a62c5"},"value":0},"geostore":"beb8e2f26bd26406fcf2018d343a62c5","id":"f1dd79c3-e6d4-4d8c-b164-b4bd66f311ee","type":"glad-alerts"}}
    return response(200, content, headers, None, 5, request)

@urlmatch(path=r'.*/query.*')
def query_mock(url, request):
    headers = {'content-type': 'application/json'}
    content = {"data": [{"MAX(year)": 123, "MAX(julian_day)": 123, "MIN(year)": 123, "MIN(julian_day)": 123, "COUNT(julian_day)": 123}]}
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

    def glad_query_params(self):

        agg_values = ['day', 'week', 'month', 'year', 'quarter']

        glad_periods = [
            '2015-01-01,2015-12-30',
            '2016-01-01,2016-12-30',
            '2017-01-01,2017-12-30',
            '2015-01-01,2016-12-30',
            '2016-01-01,2017-12-30',
            '2015-01-01,2017-12-30'
            ]

        return agg_values, glad_periods

    def glad_path_params(self):

        land_uses = ['logging', 'mining', 'oilpalm', 'fiber']

        return land_uses

    def make_request(self, request):
        '''general method to make request using HTTMock'''

        with HTTMock(query_mock):
            with HTTMock(geostore_mock):
                response = self.app.get(request, follow_redirects=True)
                status_code = response.status_code
                data = self.deserialize(response, status_code)

                return data, status_code

    def deserialize(self, response, status_code):
        '''get json from request/ separate by status code'''

        if status_code == 200:
            return json.loads(response.data).get('data', None)
        elif status_code == 400:
            return json.loads(response.data).get('errors', None)

    def assertions(self, data, status_code, code, key, value):

        self.assertEqual(status_code, code)

        if status_code == 400:
            self.assertEqual(data[0].get(key), value)
        else:
            self.assertEqual(data.get(key), value)

    def test_geostore_notfound(self):
        '''test geostore error message'''

        logging.info('[TEST]: Beginning Glad Geostore NotFound Test')
        data, status_code = self.make_request('/api/v2/ms/glad-alerts')
        logging.info('[TEST]: response deserialized: {}'.format(data))

        self.assertions(data, status_code, 400, 'detail', 'Geostore or geojson must be set')

    def test_geostore(self):
        '''test request with geostore only'''

        logging.info('[TEST]: Beginning Glad Geostore Test')
        local_url = '{}'.format(os.getenv('LOCAL_URL'))
        data, status_code = self.make_request('/api/v2/ms/glad-alerts?geostore=beb8e2f26bd26406fcf2018d343a62c5')
        logging.info('[TEST]: response deserialized: {}'.format(data))

        self.assertions(data, status_code, 200, 'geostore', 'beb8e2f26bd26406fcf2018d343a62c5')

    def test_geostore_and_periods(self):
        '''test request with geostore and glad periods'''

        logging.info('[TEST]: Beginning Glad Geostore Test')
        local_url = '{}'.format(os.getenv('LOCAL_URL'))
        for period in self.glad_query_params()[1]:
            data, status_code = self.make_request('/api/v2/ms/glad-alerts?geostore=beb8e2f26bd26406fcf2018d343a62c5&period={}'.format(period))
            logging.info('[TEST]: response deserialized: {}'.format(data))

            self.assertions(data, status_code, 200, 'geostore', 'beb8e2f26bd26406fcf2018d343a62c5')

    def test_admin_and_periods(self):
        '''test request with admin and periods'''

        logging.info('[TEST]: Beginning Glad Admin Test')
        local_url = '{}'.format(os.getenv('LOCAL_URL'))
        for period in self.glad_query_params()[1]:
            data, status_code = self.make_request('/api/v2/ms/glad-alerts/admin/per/1?period={}'.format(period))
            logging.info('[TEST]: response deserialized: {}'.format(data))

            self.assertions(data, status_code, 200, 'type', 'glad-alerts')

    def test_use_and_periods(self):
        '''test request land use and glad periods'''

        logging.info('[TEST]: Beginning Glad Use Test')
        local_url = '{}'.format(os.getenv('LOCAL_URL'))
        for period in self.glad_query_params()[1]:
            for use in self.glad_path_params():
                data, status_code = self.make_request('/api/v2/ms/glad-alerts/use/{0}/100?period={1}'.format(use, period))
                logging.info('[TEST]: response deserialized: {}'.format(data))

                self.assertions(data, status_code, 200, 'type', 'glad-alerts')

    def test_wdpa_and_periods(self):
        '''test request with wdpa and glad periods'''

        logging.info('[TEST]: Beginning Glad WDPA Test')
        local_url = '{}'.format(os.getenv('LOCAL_URL'))
        for period in self.glad_query_params()[1]:
            data, status_code = self.make_request('/api/v2/ms/glad-alerts/wdpa/100?period={}'.format(period))
            logging.info('[TEST]: response deserialized: {}'.format(data))

            self.assertions(data, status_code, 200, 'type', 'glad-alerts')

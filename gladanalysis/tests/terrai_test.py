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
    content = {"data":{"attributes":{"areaHa":231065643.70829132,"downloadUrls":{"csv":"/download/1dca5597-d6ac-4064-82cf-9f02b178f424?sql=SELECT lat, long, country_iso, state_id, dist_id, year, day FROM index_1dca5597d6ac406482cf9f02b178f424 WHERE ((year = 2004 and day >= 161) or (year >= 2005 and year <= 2016) or (year = 2017 and day <= 81))ORDER BY year, day&format=csv&geostore=141cba8b4aadde4a5b981917214666e0","json":"/download/1dca5597-d6ac-4064-82cf-9f02b178f424?sql=SELECT lat, long, country_iso, state_id, dist_id, year, day FROM index_1dca5597d6ac406482cf9f02b178f424 WHERE ((year = 2004 and day >= 161) or (year >= 2005 and year <= 2016) or (year = 2017 and day <= 81))ORDER BY year, day&format=json&geostore=141cba8b4aadde4a5b981917214666e0"},"value":1000},"geostore":"141cba8b4aadde4a5b981917214666e0","id":"1dca5597-d6ac-4064-82cf-9f02b178f424","type":"terrai-alerts"}}
    return response(200, content, headers, None, 5, request)

@urlmatch(path=r'.*/query.*')
def query_mock(url, request):
    headers = {'content-type': 'application/json'}
    content = content = {"data": [{"MAX(year)": 123, "MAX(day)": 123, "MIN(year)": 123, "MIN(day)": 123, "COUNT(day)": 123}]}
    return response(200, content, headers, None, 5, request)

class TerraiTest(unittest.TestCase):

    def setUp(self):
        app = create_application()
        app.testing = True
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def tearDown(self):
        pass

    def terrai_query_params(self):

        agg_values = ['day', 'week', 'month', 'year', 'quarter']

        terrai_periods = [
            '2004-01-01,2004-12-30',
            '2005-01-01,2005-12-30',
            '2006-01-01,2006-12-30',
            '2007-01-01,2007-12-30',
            '2008-01-01,2008-12-30',
            '2009-01-01,2009-12-30',
            '2010-01-01,2010-12-30',
            '2011-01-01,2011-12-30',
            '2012-01-01,2012-12-30',
            '2013-01-01,2013-12-30',
            '2014-01-01,2014-12-30',
            '2015-01-01,2015-12-30',
            '2016-01-01,2016-12-30',
            '2017-01-01,2017-12-30'
            ]

        return agg_values, terrai_periods

    def terrai_path_params(self):

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

        logging.info('[TEST]: Beginning terrai Geostore NotFound Test')
        data, status_code = self.make_request('/api/v2/ms/terrai-alerts')
        logging.info('[TEST]: response deserialized: {}'.format(data))

        self.assertions(data, status_code, 400, 'detail', 'Geostore or geojson must be set')

    def test_geostore(self):
        '''test request with geostore only'''

        logging.info('[TEST]: Beginning terrai Geostore Test')
        local_url = '{}'.format(os.getenv('LOCAL_URL'))
        data, status_code = self.make_request('/api/v2/ms/terrai-alerts?geostore=beb8e2f26bd26406fcf2018d343a62c5')
        logging.info('[TEST]: response deserialized: {}'.format(data))

        self.assertions(data, status_code, 200, 'geostore', 'beb8e2f26bd26406fcf2018d343a62c5')

    def test_geostore_and_periods(self):
        '''test request with geostore and Terrai periods'''

        logging.info('[TEST]: Beginning Terrai Geostore Test')
        local_url = '{}'.format(os.getenv('LOCAL_URL'))
        for period in self.terrai_query_params()[1]:
            data, status_code = self.make_request('/api/v2/ms/terrai-alerts?geostore=beb8e2f26bd26406fcf2018d343a62c5&period={}'.format(period))
            logging.info('[TEST]: response deserialized: {}'.format(data))

            self.assertions(data, status_code, 200, 'geostore', 'beb8e2f26bd26406fcf2018d343a62c5')

    def test_admin_and_periods(self):
        '''test request with admin and periods'''

        logging.info('[TEST]: Beginning terrai Admin Test')
        local_url = '{}'.format(os.getenv('LOCAL_URL'))
        for period in self.terrai_query_params()[1]:
            data, status_code = self.make_request('/api/v2/ms/terrai-alerts/admin/per/1?period={}'.format(period))
            logging.info('[TEST]: response deserialized: {}'.format(data))

            self.assertions(data, status_code, 200, 'type', 'terrai-alerts')

    def test_use_and_periods(self):
        '''test request land use and terrai periods'''

        logging.info('[TEST]: Beginning terrai Use Test')
        local_url = '{}'.format(os.getenv('LOCAL_URL'))
        for period in self.terrai_query_params()[1]:
            for use in self.terrai_path_params():
                data, status_code = self.make_request('/api/v2/ms/terrai-alerts/use/{0}/100?period={1}'.format(use, period))
                logging.info('[TEST]: response deserialized: {}'.format(data))

                self.assertions(data, status_code, 200, 'type', 'terrai-alerts')

    def test_wdpa_and_periods(self):
        '''test request with wdpa and terrai periods'''

        logging.info('[TEST]: Beginning terrai WDPA Test')
        local_url = '{}'.format(os.getenv('LOCAL_URL'))
        for period in self.terrai_query_params()[1]:
            data, status_code = self.make_request('/api/v2/ms/terrai-alerts/wdpa/100?period={}'.format(period))
            logging.info('[TEST]: response deserialized: {}'.format(data))

            self.assertions(data, status_code, 200, 'type', 'terrai-alerts')

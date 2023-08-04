import json
import logging
import os
import unittest
import requests_mock
from moto import mock_logs
from gladanalysis import create_application
from gladanalysis.tests.mocks import mock_geostore, mock_geostore_not_found, mock_query
from RWAPIMicroservicePython.test_utils import mock_request_validation


@mock_logs
class TerraiTest(unittest.TestCase):

    def setUp(self):
        app = create_application()
        app.config.update({
            "TESTING": True,
        })
        self.app = app.test_client()

    def tearDown(self):
        pass

    @staticmethod
    def terrai_query_params():
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

    @staticmethod
    def terrai_path_params():
        land_uses = ['logging', 'mining', 'oilpalm', 'fiber']
        return land_uses

    def make_request(self, request):
        try:
            response = self.app.get(request, follow_redirects=True, headers={'x-api-key': 'api-key-test'})
            status_code = response.status_code
            data = self.deserialize(response, status_code)

            return data, status_code
        except Exception as e:
            logging.error(e)
            raise e

    @staticmethod
    def deserialize(response, status_code):
        """get json from request/ separate by status code"""

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

    @requests_mock.mock(kw='mocker')
    def test_geostore_notfound(self, mocker):
        """test geostore error message"""
        mock_request_validation(mocker, microservice_token=os.getenv('MICROSERVICE_TOKEN'))
        mock_geostore_not_found(mocker)

        logging.info('[TEST]: Beginning terrai Geostore NotFound Test')
        data, status_code = self.make_request('/api/v2/ms/terrai-alerts')
        logging.info('[TEST]: response deserialized: {}'.format(data))

        self.assertions(data, status_code, 400, 'detail', 'Geostore or geojson must be set')

    @requests_mock.mock(kw='mocker')
    def test_geostore(self, mocker):
        """test request with geostore only"""
        mock_request_validation(mocker, microservice_token=os.getenv('MICROSERVICE_TOKEN'))
        mock_query(mocker)
        mock_geostore(mocker)
        logging.info('[TEST]: Beginning terrai Geostore Test')
        data, status_code = self.make_request('/api/v2/ms/terrai-alerts?geostore=beb8e2f26bd26406fcf2018d343a62c5')
        logging.info('[TEST]: response deserialized: {}'.format(data))

        self.assertions(data, status_code, 200, 'geostore', 'beb8e2f26bd26406fcf2018d343a62c5')

    @requests_mock.mock(kw='mocker')
    def test_geostore_and_periods(self, mocker):
        """test request with geostore and Terrai periods"""
        mock_request_validation(mocker, microservice_token=os.getenv('MICROSERVICE_TOKEN'))
        mock_query(mocker)
        mock_geostore(mocker)

        logging.info('[TEST]: Beginning Terrai Geostore Test')
        for period in self.terrai_query_params()[1]:
            data, status_code = self.make_request(
                '/api/v2/ms/terrai-alerts?geostore=beb8e2f26bd26406fcf2018d343a62c5&period={}'.format(period))
            logging.info('[TEST]: response deserialized: {}'.format(data))

            self.assertions(data, status_code, 200, 'geostore', 'beb8e2f26bd26406fcf2018d343a62c5')

    @requests_mock.mock(kw='mocker')
    def test_admin_and_periods(self, mocker):
        """test request with admin and periods"""
        mock_query(mocker)
        mock_geostore(mocker)
        mock_request_validation(mocker, microservice_token=os.getenv('MICROSERVICE_TOKEN'))
        logging.info('[TEST]: Beginning terrai Admin Test')
        for period in self.terrai_query_params()[1]:
            data, status_code = self.make_request('/api/v2/ms/terrai-alerts/admin/per/1?period={}'.format(period))
            logging.info('[TEST]: response deserialized: {}'.format(data))

            self.assertions(data, status_code, 200, 'type', 'terrai-alerts')

    @requests_mock.mock(kw='mocker')
    def test_use_and_periods(self, mocker):
        """test request land use and terrai periods"""
        mock_request_validation(mocker, microservice_token=os.getenv('MICROSERVICE_TOKEN'))
        mock_query(mocker)
        mock_geostore(mocker)

        logging.info('[TEST]: Beginning terrai Use Test')
        for period in self.terrai_query_params()[1]:
            for use in self.terrai_path_params():
                data, status_code = self.make_request(
                    '/api/v2/ms/terrai-alerts/use/{0}/100?period={1}'.format(use, period))
                logging.info('[TEST]: response deserialized: {}'.format(data))

                self.assertions(data, status_code, 200, 'type', 'terrai-alerts')

    @requests_mock.mock(kw='mocker')
    def test_wdpa_and_periods(self, mocker):
        """test request with wdpa and terrai periods"""
        mock_request_validation(mocker, microservice_token=os.getenv('MICROSERVICE_TOKEN'))
        mock_query(mocker)
        mock_geostore(mocker)

        logging.info('[TEST]: Beginning terrai WDPA Test')
        for period in self.terrai_query_params()[1]:
            data, status_code = self.make_request('/api/v2/ms/terrai-alerts/wdpa/100?period={}'.format(period))
            logging.info('[TEST]: response deserialized: {}'.format(data))

            self.assertions(data, status_code, 200, 'type', 'terrai-alerts')

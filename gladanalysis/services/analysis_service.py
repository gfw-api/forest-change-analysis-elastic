from RWAPIMicroservicePython import request_to_microservice
from flask import request


class AnalysisService(object):
    """Class for sending queries to databases and capturing response
    Methods take sql and geostore or geojson arguments, which are used to query the
    elastic search database and return a response in json"""

    @staticmethod
    def make_analysis_request(dataset_id, sql, geostore, geojson, api_key, v2=False):

        if request.method == 'GET':
            uri = "/query/" + dataset_id + '?sql=' + sql + '&format=json'

            if geostore:
                uri += "&geostore=" + geostore

            config = {
                'uri': uri,
                'method': 'GET',
                'api_key': api_key
            }

        else:
            uri = "/query/" + dataset_id

            body = {'sql': sql,
                    'format': 'json',
                    'geojson': geojson}

            config = {
                'uri': uri,
                'method': 'POST',
                'body': body,
                'api_key': api_key
            }

        if v2:
            config = {
                'uri': "/v2/query/23285d52-a4b9-4f5a-a9d6-158c4bbc0f86",
                'method': 'POST',
                'body': {'sql': 'select count(*) FROM index_d6268f65e4cf4a1a9435fb52a1c7ddd0',
                         'format': 'json',
                         'geojson': geojson},
                'api_key': api_key
            }

        return request_to_microservice(**config)

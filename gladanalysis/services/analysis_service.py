import json
import os
from CTRegisterMicroserviceFlask import request_to_microservice

class AnalysisService(object):
    """Class for sending queries to databases and capturing response"""

    @staticmethod
    def make_glad_request(sql, geostore=None):

        uri = "/query/" + os.getenv('GLAD_DATASET_ID') + sql + '&format=json'

        if geostore:
            uri += "&geostore=" + geostore

        config = {
        'uri': uri,
        'method': 'GET'
        }
        #if geojson make post
        
        return request_to_microservice(config)

    @staticmethod
    def make_terrai_request(sql, geostore=None):

        uri = "/query/" + os.getenv('TERRAI_DATASET_ID') + sql + '&format=json'

        if geostore:
            uri += "&geostore=" + geostore

        config = {
        'uri': uri,
        'method': 'GET'
        }

        return request_to_microservice(config)

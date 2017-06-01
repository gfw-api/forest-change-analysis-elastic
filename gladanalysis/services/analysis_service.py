import requests
import json
import os
from CTRegisterMicroserviceFlask import request_to_microservice

class AnalysisService(object):
    """Class for sending queries to databases and capturing response"""

    @staticmethod
    def make_glad_request(sql, geostore=None):

        uri = "/query/" + os.getenv('GLAD_DATASET_ID') + sql + '&format=json'


        #format request to glad dataset
        # url = 'http://staging-api.globalforestwatch.org/query/'
        # datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
        # f = '&format=json'

        if geostore:
            uri += "&geostore=" + geostore
            #full = url + datasetID + sql + "&geostore=" + geostore + f
        #else:
            #full = url + datasetID + sql + f

        config = {
        'uri': uri,
        'method': 'GET'
        }

        return request_to_microservice(config)

    @staticmethod
    def make_terrai_request(sql, geostore=None):

        #format request to glad dataset
        url = 'http://staging-api.globalforestwatch.org/query/'
        datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
        f = '&format=json'

        if geostore:
            full = url + datasetID + sql + "&geostore=" + geostore + f
        else:
            full = url + datasetID + sql + f

        r = requests.get(url=full)
        data = r.json()
        return data

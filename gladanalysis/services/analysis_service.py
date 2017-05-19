import requests
import json
import os

class AnalysisService(object):

    @staticmethod
    def make_glad_request(sql, confidence, geostore=None):

        #format request to glad dataset
        url = 'http://staging-api.globalforestwatch.org/query/'
        datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
        f = '&format=json'

        if geostore:
            full = url + datasetID + sql + confidence + "&geostore=" + geostore + f
        else:
            full = url + datasetID + sql + confidence + f

        r = requests.get(url=full)
        data = r.json()
        return data

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

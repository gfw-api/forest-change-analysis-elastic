import json
import os
import logging

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

        return request_to_microservice(config)

    @staticmethod
    def make_glad_request_post(sql, geojson):

        uri = "/query/" + os.getenv('GLAD_DATASET_ID')

        if not geojson:
            return error(status=400, detail="Geojson must be inlcuded in body")

        body = {'sql': sql,
                'format': 'json',
                'geojson': geojson}

        config = {
        'uri': uri,
        'method': 'POST',
        'body': body
        }

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

    @staticmethod
    def make_terrai_request_post(sql, geojson):

        uri = "/query/" + os.getenv('TERRAI_DATASET_ID')

        if not geojson:
            return error(status=400, detail="Geojson must be inlcuded in body")

        body = {'sql': sql,
                'format': 'json',
                'geojson': geojson}

        config = {
        'uri': uri,
        'method': 'POST',
        'body': body
        }

        return request_to_microservice(config)

import json
import os
import logging
from flask import request

from CTRegisterMicroserviceFlask import request_to_microservice

from gladanalysis.routes.api.v2 import error

class AnalysisService(object):
    """Class for sending queries to databases and capturing response
    Methods take sql and geostore or geojson arguments, which are used to query the
    elastic search database and return a response in json"""

    @staticmethod
    def make_analysis_request(dataset_id, sql, geostore, geojson):

        if request.method == 'GET':
            uri = "/query/" + dataset_id + '?sql=' + sql + '&format=json'

            if geostore:
                uri += "&geostore=" + geostore

            config = {
            'uri': uri,
            'method': 'GET'
            }

        else:
            uri = "/query/" + dataset_id

            body = {'sql': sql,
                    'format': 'json',
                    'geojson': geojson}

            config = {
            'uri': uri,
            'method': 'POST',
            'body': body
            }

        return request_to_microservice(config)

import json
from flask import request

from CTRegisterMicroserviceFlask import request_to_microservice
from gladanalysis.errors import GeostoreNotFound

class GeostoreService(object):
    """Class for sending request to geostore (to fetch area in hectares and geostore id)"""

    @staticmethod
    def execute(uri):

        config = {
        'uri': uri,
        'method': 'GET'
        }

        try:
            response = request_to_microservice(config)
        except Exception as e:
            raise Exception(str(e))

        if response.get('errors'):
            error = response.get('errors')[0]
            if error.get('status') == 404:
                raise GeostoreNotFound(message='')
            else:
                raise Exception(error.get('detail'))

        return response

    @staticmethod
    def make_use_request(use_type, use_id):

        uri = "/geostore/use/%s/%s" %(use_type, use_id)
        geostore_data = GeostoreService.execute(uri)

        geostore = geostore_data['data']['id']
        area = geostore_data['data']['attributes']['areaHa']
        return (geostore, area)

    @staticmethod
    def make_gadm_request(iso_code, admin_id=None, dist_id=None):

        if not admin_id and not dist_id:
            uri = "/geostore/admin/%s" %(iso_code)

        elif admin_id and not dist_id:
            uri = "/geostore/admin/%s/%s" %(iso_code, admin_id)

        elif admin_id and dist_id:
            uri = "/geostore/admin/%s/%s/%s" %(iso_code, admin_id, dist_id)

        geostore_data = GeostoreService.execute(uri)
        area_ha = geostore_data['data']['attributes']['areaHa']
        return area_ha

    @staticmethod
    def make_area_request(geostore):

        uri = "/geostore/%s" %(geostore)
        area_resp = GeostoreService.execute(uri)

        area = area_resp['data']['attributes']['areaHa']
        return area

    @staticmethod
    def make_wdpa_request(wdpa_id):

        uri = "/geostore/wdpa/%s" %(wdpa_id)
        geostore_data = GeostoreService.execute(uri)

        geostore = geostore_data['data']['id']
        area = geostore_data['data']['attributes']['areaHa']
        return (geostore, area)

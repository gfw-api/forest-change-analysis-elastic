import json
from CTRegisterMicroserviceFlask import request_to_microservice

class GeostoreService(object):
    """Class for sending request to geostore (to fetch area in hectares and geostore id)"""

    @staticmethod
    def execute(uri):

        config = {
        'uri': uri,
        'method': 'GET'
        }

        return request_to_microservice(config)

    def make_use_request(use_type, use_id):

        uri = "/geostore/use/%s/%s" %(use_type, use_id)

        geostore_data = self.execute(uri)
        geostore = geostore_data['data']['id']
        area = geostore_data['data']['attributes']['areaHa']
        return (geostore, area)

    def make_gadm_request(iso_code, admin_id=None, dist_id=None):

        if not admin_id and not dist_id:
            uri = "/geostore/admin/%s" %(iso_code)

        elif admin_id and not dist_id:
            uri = "/geostore/admin/%s/%s" %(iso_code, admin_id)

        elif admin_id and dist_id:
            uri = "/geostore/admin/%s/%s/%s" %(iso_code, admin_id, dist_id)

        geostore_data = self.execute(uri)
        area_ha = geostore_data['data']['attributes']['areaHa']
        return area_ha

    def make_area_request(geostore):

        uri = "/geostore/%s" %(geostore)
        area_resp = self.execute(uri)
        area = area_resp['data']['attributes']['areaHa']
        return area

    def make_wdpa_request(wdpa_id):

        uri = "/geostore/wdpa/%s" %(wdpa_id)
        geostore_data = self.execute(uri)
        geostore = geostore_data['data']['id']
        area = geostore_data['data']['attributes']['areaHa']
        return (geostore, area)

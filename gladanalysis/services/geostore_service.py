from RWAPIMicroservicePython import request_to_microservice

from gladanalysis.errors import GeostoreNotFound


class GeostoreService(object):
    """Class for sending request to geostore (to fetch area in hectares and geostore id)"""

    @staticmethod
    def execute(uri, api_key):
        try:
            response = request_to_microservice(uri=uri, method='GET', api_key=api_key)
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
    def make_use_request(use_type, use_id, api_key):

        uri = "/v2/geostore/use/%s/%s" % (use_type, use_id)
        geostore_data = GeostoreService.execute(uri, api_key)

        geostore = geostore_data['data']['id']
        area = geostore_data['data']['attributes']['areaHa']
        return (geostore, area)

    @staticmethod
    def make_gadm_request(iso_code, api_key, admin_id=None, dist_id=None):
        if not admin_id and not dist_id:
            uri = "/v2/geostore/admin/%s?simplify=0.05" % iso_code

        elif admin_id and not dist_id:
            uri = "/v2/geostore/admin/%s/%s" % (iso_code, admin_id)

        elif admin_id and dist_id:
            uri = "/v2/geostore/admin/%s/%s/%s" % (iso_code, admin_id, dist_id)

        geostore_data = GeostoreService.execute(uri, api_key)
        area_ha = geostore_data['data']['attributes']['areaHa']
        return area_ha

    @staticmethod
    def make_area_request(geostore, api_key):
        uri = "/v2/geostore/%s" % geostore
        area_resp = GeostoreService.execute(uri, api_key)

        area = area_resp['data']['attributes']['areaHa']
        return area

    @staticmethod
    def make_wdpa_request(wdpa_id, api_key):
        uri = "/v2/geostore/wdpa/%s" % (wdpa_id)
        geostore_data = GeostoreService.execute(uri, api_key)

        geostore = geostore_data['data']['id']
        area = geostore_data['data']['attributes']['areaHa']
        return geostore, area

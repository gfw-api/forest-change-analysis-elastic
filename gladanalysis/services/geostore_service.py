import json
import requests


class GeostoreService(object):

    @staticmethod
    def make_use_request(use_type, use_id):

        area_url = 'http://staging-api.globalforestwatch.org/geostore/use/%s/%s' %(use_type, use_id)
        r = requests.get(url=area_url)
        geostore_data = r.json()
        geostore = geostore_data['data']['id']
        area = geostore_data['data']['attributes']['areaHa']
        return (geostore, area)

    @staticmethod
    def make_gadm_request(iso_code, admin_id=None, dist_id=None):

        if not admin_id and not dist_id:
            geostore_url = 'https://staging-api.globalforestwatch.org/geostore/admin/%s'%(iso_code)

        elif admin_id and not dist_id:
            geostore_url = 'https://staging-api.globalforestwatch.org/geostore/admin/%s/%s'%(iso_code, admin_id)

        elif admin_id and dist_id:
            geostore_url = 'https://staging-api.globalforestwatch.org/geostore/admin/%s/%s/%s'%(iso_code, admin_id, dist_id)

        r = requests.get(url=geostore_url)
        geostore_data = r.json()
        geostore = geostore_data['data']['id']
        area_ha = geostore_data['data']['attributes']['areaHa']
        return area_ha

    @staticmethod
    def make_area_request(geostore):

        area_url = 'http://staging-api.globalforestwatch.org/geostore/' + geostore
        r_area = requests.get(url=area_url)
        area_resp = r_area.json()
        area = area_resp['data']['attributes']['areaHa']
        return area

    @staticmethod
    def make_wdpa_request(wdpa_id):

        area_url = 'http://staging-api.globalforestwatch.org/geostore/wdpa/%s' %(wdpa_id)
        r = requests.get(url=area_url)
        geostore_data = r.json()
        geostore = geostore_data['data']['id']
        area = geostore_data['data']['attributes']['areaHa']
        return (geostore, area)

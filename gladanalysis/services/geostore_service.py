import json
import requests 


class GeostoreService(object):

    def make_use_request(use_type, use_id):

        area_url = 'http://staging-api.globalforestwatch.org/geostore/use/%s/%s' %(use_type, use_id)
        r = requests.get(url=area_url)
        geostore_data = r.json()
        geostore = geostore_data['data']['id']
        area = geostore_data['data']['attributes']['areaHa']
        return (geostore, area)

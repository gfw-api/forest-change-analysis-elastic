import os
import logging

class ResponseService(object):
    """Class for standardizing api responses"""

    @staticmethod
    def standardize_response(name, data, datasetID, count=None, download_sql=None, area=None, geostore=None, agg=None, agg_by=None, period=None):
        #Helper function to standardize API responses
        standard_format = {}
        if name == 'Glad':
            standard_format["type"] = "glad-alerts"
            standard_format["id"] = '{}'.format(os.getenv('GLAD_DATASET_ID'))
        elif name == 'Terrai':
            standard_format["type"] = "terrai-alerts"
            standard_format["id"] = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
        if period:
            standard_format['period'] = period
        standard_format["attributes"] = {}
        if agg:
            standard_format['aggregate_values'] = True
            years = data.keys()
            for year in years:
                standard_format["attributes"][year] = data[year]
        if agg_by:
            standard_format['aggregate_by'] = agg_by
        elif agg == None:
            standard_format["attributes"]["value"] = data["data"][0][count]
        if download_sql:
            standard_format["attributes"]["downloadUrls"] = {}
            standard_format["attributes"]["downloadUrls"]["csv"] = "/download/" + datasetID + download_sql + "&format=csv"
            standard_format["attributes"]["downloadUrls"]["json"] = "/download/" + datasetID + download_sql + "&format=json"
        if geostore:
            standard_format["geostore"] = geostore
            standard_format["attributes"]["downloadUrls"]["csv"] += "&geostore=" + geostore
            standard_format["attributes"]["downloadUrls"]["json"] += "&geostore=" + geostore
        if area:
            standard_format['attributes']["areaHa"] = area

        return standard_format

    @staticmethod
    def format_date_range(name, min_date, max_date):
        response = {}
        if name == 'Glad':
            response['type'] = 'glad-alerts'
            response['id'] = '{}'.format(os.getenv('GLAD_DATASET_ID'))
        elif name == 'Terrai':
            response['type'] = 'terrai-alerts'
            response['id'] = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
        response['attributes'] = {}
        response['attributes']['minDate'] = min_date
        response['attributes']['maxDate'] = max_date

        return response

    @staticmethod
    def format_latest_date(name, max_date):
        response = []
        info = {}
        if name == 'Glad':
            info['type'] = 'glad-alerts'
            info['id'] = '{}'.format(os.getenv('GLAD_DATASET_ID'))
        elif name == 'Terrai':
            info['type'] = 'terrai-alerts'
            info['id'] = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
        info['attributes'] = {}
        info['attributes']['date'] = max_date

        response.append(info)

        return response

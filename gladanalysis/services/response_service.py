import os


class ResponseService(object):
    """Class for standardizing api responses"""

    @staticmethod
    def standardize_response(name, data, datasetID, count=None, download_sql=None, area=None, geostore=None, agg=None,
                             agg_by=None, period=None):
        # Helper function to standardize API responses
        standard_format = {}
        standard_format["type"] = "terrai-alerts"
        standard_format["id"] = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
        if period:
            standard_format['period'] = period
        standard_format["attributes"] = {}
        if agg:
            standard_format['aggregate_values'] = True
            standard_format["attributes"]["value"] = data

        if agg_by:
            standard_format['aggregate_by'] = agg_by
        else:
            standard_format["attributes"]["value"] = list(data["data"][0].values())[0]

        if download_sql:
            standard_format["attributes"]["downloadUrls"] = {}
            standard_format["attributes"]["downloadUrls"][
                "csv"] = "/download/" + datasetID + download_sql + "&format=csv"
            standard_format["attributes"]["downloadUrls"][
                "json"] = "/download/" + datasetID + download_sql + "&format=json"
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
        info['type'] = 'terrai-alerts'
        info['id'] = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
        info['attributes'] = {}
        info['attributes']['date'] = max_date

        response.append(info)

        return response



class ResponseService(object):

    @staticmethod
    def standardize_response(data, count, datasetID, download_sql, area, geostore=None):
        #Helper function to standardize API responses
        standard_format = {}
        standard_format["type"] = "glad-alerts"
        standard_format["id"] = "undefined"
        standard_format["attributes"] = {}
        standard_format["attributes"]["value"] = data["data"][0][count]
        standard_format["attributes"]["downloadUrls"] = {}
        if geostore:
            standard_format["attributes"]["downloadUrls"]["csv"] = "/download/" + datasetID + download_sql + "&geostore=" + geostore + "&format=csv"
            standard_format["attributes"]["downloadUrls"]["json"] = "/download/" + datasetID + download_sql + "&geostore=" + geostore + "&format=json"
        else:
            standard_format["attributes"]["downloadUrls"]["csv"] = "/download/" + datasetID + download_sql + "&format=csv"
            standard_format["attributes"]["downloadUrls"]["json"] = "/download/" + datasetID + download_sql + "&format=json"
        standard_format['attributes']["areaHa"] = area

        return standard_format

    @staticmethod
    def format_date_range(min_date, max_date):

        response = {}
        response['type'] = "terrai-alerts"
        response['id'] = "undefined"
        response['attributes'] = {}
        response['attributes']['minDate'] = min_date
        response['attributes']['maxDate'] = max_date

        return response

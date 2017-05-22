

class ResponseService(object):

    @staticmethod
    def standardize_response(name, data, count, datasetID, download_sql, area, geostore=None):
        #Helper function to standardize API responses
        standard_format = {}
        if name == 'Glad':
            standard_format["type"] = "glad-alerts"
            standard_format["id"] = '{}'.format(os.getenv('GLAD_DATASET_ID'))
        elif name == 'Terrai':
            standard_format["type"] = "terrai-alerts"
            standard_format["id"] = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
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

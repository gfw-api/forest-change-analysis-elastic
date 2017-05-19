import os
import logging
import datetime

from flask import jsonify, request
import requests

from . import endpoints
from gladanalysis.services import GeostoreService
from gladanalysis.services import DateService
from gladanalysis.services import SqlService
from gladanalysis.responders import ErrorResponder
from gladanalysis.utils.http import request_to_microservice
from gladanalysis.validators import validate_geostore, validate_period, validate_admin, validate_use, validate_wdpa

def make_glad_request(sql, confidence, geostore=None):

    #format request to glad dataset
    url = 'http://staging-api.globalforestwatch.org/query/'
    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    f = '&format=json'

    if geostore:
        full = url + datasetID + sql + confidence + "&geostore=" + geostore + f
    else:
        full = url + datasetID + sql + confidence + f

    r = requests.get(url=full)
    data = r.json()
    return data

def make_terrai_request(sql, geostore=None):

    #format request to glad dataset
    url = 'http://staging-api.globalforestwatch.org/query/'
    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    f = '&format=json'

    if geostore:
        full = url + datasetID + sql + "&geostore=" + geostore + f
    else:
        full = url + datasetID + sql + f

    r = requests.get(url=full)
    data = r.json()
    return data

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

@endpoints.route('/gladanalysis', methods=['GET'])
@validate_geostore
@validate_period

def query_glad():
    """Query GLAD"""
    logging.info('QUERYING GLAD')

    geostore = request.args.get('geostore', None)
    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #send to sql formatter function
    sql, download_sql = SqlService.format_glad_sql(from_year, from_date, to_year, to_date)

    #create condition to look for confidence filter
    if conf == 'true' or conf == 'True':
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    #query glad database
    data = make_glad_request(sql, confidence, geostore)

    #make request to geostore to get area in hectares
    area = GeostoreService.make_area_request(geostore)

    #standardize response
    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    standard_format = standardize_response(data, "COUNT(julian_day)", datasetID, download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200


@endpoints.route('/terraianalysis', methods=['GET'])
@validate_geostore
@validate_period

def query_terrai():

    logging.info('QUERYING TERRA I')

    geostore = request.args.get('geostore', None)
    period = request.args.get('period', None)

    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #create conditions that issue correct sql
    sql, download_sql = SqlService.format_terrai_sql(from_year, from_date, to_year, to_date)

    #format request parameters to Terra I
    data = make_terrai_request(sql, geostore)

    #get area from geostore
    area = GeostoreService.make_area_request(geostore)

    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    standard_format = standardize_response(data, "COUNT(day)", datasetID, download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/gladanalysis/admin/<iso_code>/<admin_id>/<dist_id>', methods=['GET'])
@validate_period
@validate_admin

def glad_dist(iso_code, admin_id, dist_id):

    logging.info('Running GADM level glad analysis')

    #accept period parameter
    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #send to sql formatter function
    sql, download_sql = SqlService.format_glad_sql(from_year, from_date, to_year, to_date, iso_code, admin_id, dist_id)

    area_ha = GeostoreService.make_gadm_request(iso_code, admin_id)

    if conf == 'true' or conf == "True":
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    #query glad database
    data = make_glad_request(sql, confidence)

    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    standard_format = standardize_response(data, "COUNT(julian_day)", datasetID, download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/gladanalysis/admin/<iso_code>/<admin_id>', methods=['GET'])
@validate_period
@validate_admin

def glad_admin(iso_code, admin_id):

    logging.info('Running GADM level glad analysis')

    #accept period parameter
    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #send to sql formatter function
    sql, download_sql = SqlService.format_glad_sql(from_year, from_date, to_year, to_date, iso_code, admin_id)

    #get geostore id from admin areas and total area of geostore request
    area_ha = GeostoreService.make_gadm_request(iso_code, admin_id)

    if conf == 'true' or conf == "True":
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    #query glad database
    data = make_glad_request(sql, confidence)

    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    standard_format = standardize_response(data, "COUNT(julian_day)", datasetID, download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/gladanalysis/admin/<iso_code>', methods=['GET'])
@validate_period
@validate_admin

def glad_country(iso_code):

    logging.info('Running country level glad analysis')

    #accept period parameter
    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #send to sql formatter function
    sql, download_sql = SqlService.format_glad_sql(from_year, from_date, to_year, to_date, iso_code)

    #get geostore id from admin areas and total area of geostore request
    area_ha = GeostoreService.make_gadm_request(iso_code)

    if conf == 'true' or conf == "True":
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    #make request to glad database
    data = make_glad_request(sql, confidence)

    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    standard_format = standardize_response(data, "COUNT(julian_day)", datasetID, download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terraianalysis/admin/<iso_code>/<admin_id>', methods=['GET'])
@validate_period
@validate_admin

def terrai_admin(iso_code, admin_id):
    logging.info('QUERYING TERRA I AT GADM LEVEL')

    period = request.args.get('period', None)

    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #send dates to sql formatter
    sql, download_sql = SqlService.format_terrai_sql(from_year, from_date, to_year, to_date, iso_code, admin_id)

    #get geostore id from admin areas and total area of geostore request
    area_ha = GeostoreService.make_gadm_request(iso_code, admin_id)

    #Make request to terra i dataset
    data = make_terrai_request(sql)

    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    standard_format = standardize_response(data, "COUNT(day)", datasetID, download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terraianalysis/admin/<iso_code>/<admin_id>/<dist_id>', methods=['GET'])
@validate_period
@validate_admin

def terrai_dist(iso_code, admin_id, dist_id):
    logging.info('QUERYING TERRA I AT GADM LEVEL')

    period = request.args.get('period', None)

    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #send dates to sql formatter
    sql, download_sql = SqlService.format_terrai_sql(from_year, from_date, to_year, to_date, iso_code, admin_id, dist_id)

    #get area of request
    area_ha = GeostoreService.make_gadm_request(iso_code, admin_id, dist_id)

    #Make request to terra i dataset
    data = make_terrai_request(sql)

    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    standard_format = standardize_response(data, "COUNT(day)", datasetID, download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terraianalysis/admin/<iso_code>', methods=['GET'])
@validate_period
@validate_admin

def terrai_country(iso_code):

    logging.info('QUERYING TERRA I AT COUNTRY LEVEL')

    period = request.args.get('period', None)

    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #send dates to sql formatter
    sql, download_sql = SqlService.format_terrai_sql(from_year, from_date, to_year, to_date, iso_code)

    #get geostore id from admin areas and total area of geostore request
    area_ha = GeostoreService.make_gadm_request(iso_code)

    #make request to terra i dataset
    data = make_terrai_request(sql)

    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    standard_format = standardize_response(data, "COUNT(day)", datasetID, download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/gladanalysis/use/<use_type>/<use_id>', methods=['GET'])
@validate_use
@validate_period

def glad_use(use_type, use_id):

    logging.info('QUERY GLAD BY LAND USE DATA')

    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #send to sql formatter function
    sql, download_sql = SqlService.format_glad_sql(from_year, from_date, to_year, to_date)

    geostore, area = GeostoreService.make_use_request(use_type, use_id)

    if conf == 'true' or conf == "True":
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    #make request to glad database
    data = make_glad_request(sql, confidence, geostore)

    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    standard_format = standardize_response(data, "COUNT(julian_day)", datasetID, download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terraianalysis/use/<use_type>/<use_id>', methods=['GET'])
@validate_use
@validate_period

def terrai_use(use_type, use_id):

    logging.info('QUERY GLAD BY LAND USE DATA')

    period = request.args.get('period', None)

    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #send to sql formatter function
    sql, download_sql = SqlService.format_terrai_sql(from_year, from_date, to_year, to_date)

    geostore, area = GeostoreService.make_use_request(use_type, use_id)

    #make request to glad database
    data = make_terrai_request(sql, geostore)

    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    standard_format = standardize_response(data, "COUNT(day)", datasetID, download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/gladanalysis/wdpa/<wdpa_id>', methods=['GET'])
@validate_period
@validate_wdpa

def glad_wdpa(wdpa_id):

    logging.info('QUERY GLAD BY WDPA DATA')

    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #send to sql formatter function
    sql, download_sql = SqlService.format_glad_sql(from_year, from_date, to_year, to_date)

    geostore, area = GeostoreService.make_wdpa_request(wdpa_id)

    if conf == 'true' or conf == "True":
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    #make request to glad database
    data = make_glad_request(sql, confidence, geostore)

    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    standard_format = standardize_response(data, "COUNT(julian_day)", datasetID, download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terraianalysis/wdpa/<wdpa_id>', methods=['GET'])
@validate_period
@validate_wdpa

def terrai_wdpa(wdpa_id):

    logging.info('QUERY TERRA I BY WDPA')

    period = request.args.get('period', None)

    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #send to sql formatter function
    sql, download_sql = SqlService.format_terrai_sql(from_year, from_date, to_year, to_date)

    geostore, area = GeostoreService.make_wdpa_request(wdpa_id)

    #make request to glad database
    data = make_terrai_request(sql, geostore)

    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    standard_format = standardize_response(data, "COUNT(day)", datasetID, download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/gladanalysis/date-range', methods=['GET'])
def glad_date_range():

    max_sql = '?sql=select MAX(julian_day)from {} where year = 2017'.format(os.getenv('GLAD_INDEX_ID'))
    min_sql = '?sql=select MIN(julian_day)from {} where year = 2015'.format(os.getenv('GLAD_INDEX_ID'))

    # min_julian = get_date('274b4818-be18-4890-9d10-eae56d2a82e5', min_sql, 'MIN(julian_day)')
    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    max_julian = DateService.get_date(datasetID, max_sql, 'MAX(julian_day)')

    max_value = max_julian + 1700
    # min_value = min_julian + 1500
    min_value = 1501

    max_day = datetime.datetime.strptime(str(max_value), '%y%j').date()
    min_day = datetime.datetime.strptime(str(min_value), '%y%j').date()

    max_date = max_day.strftime('%Y-%m-%d')
    min_date = min_day.strftime('%Y-%m-%d')

    response = {}
    response['type'] = "glad-alerts"
    response['id'] = "undefined"
    response['attributes'] = {}
    response['attributes']['minDate'] = min_date
    response['attributes']['maxDate'] = max_date

    return jsonify({'data': response}), 200

@endpoints.route('/terraianalysis/date-range', methods=['GET'])
def terrai_date_range():

    max_sql = '?sql=select MAX(day)from {} where year = 2017'.format(os.getenv('TERRAI_INDEX_ID'))
    min_sql = '?sql=select MIN(day)from {} where year = 2004'.format(os.getenv('TERRAI_INDEX_ID'))

    # min_julian = get_date('274b4818-be18-4890-9d10-eae56d2a82e5', min_sql, 'MIN(julian_day)')
    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    max_julian = DateService.get_date(datasetID, max_sql, 'MAX(day)')

    max_value = max_julian + 1700
    # min_value = min_julian + 1500
    # min_value = 401

    max_day = datetime.datetime.strptime(str(max_value), '%y%j').date()
    # min_day = datetime.datetime.strptime(str(min_value), '%y%j').date()

    max_date = max_day.strftime('%Y-%m-%d')
    min_date = '2004-01-01'

    response = {}
    response['type'] = "terrai-alerts"
    response['id'] = "undefined"
    response['attributes'] = {}
    response['attributes']['minDate'] = min_date
    response['attributes']['maxDate'] = max_date

    return jsonify({'data': response}), 200

import os
import logging
import datetime

from flask import jsonify, request

from . import endpoints
from gladanalysis.services import GeostoreService
from gladanalysis.services import DateService
from gladanalysis.services import QueryConstructorService
from gladanalysis.services import AnalysisService
from gladanalysis.services import ResponseService
from gladanalysis.responders import ErrorResponder
from gladanalysis.validators import validate_geostore, validate_glad_period, validate_admin, validate_use, validate_wdpa

def analyze(area=None, geostore=None, iso=None, state=None, dist=None, geojson=None):
    """analyze method to execute queries"""

    #set variables
    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    indexID = '{}'.format(os.getenv('GLAD_INDEX_ID'))

    #send sql and geostore to analysis service to query elastic database
    if request.method == 'GET':
        #get parameters from query string
        period = request.args.get('period', None)
        conf = request.args.get('gladConfirmOnly', None)
        agg_values = request.args.get('aggregate_values', None)

        if not period:
            period = None

        #format period request to julian dates
        from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period=period, datasetID=datasetID, indexID=indexID, value="julian_day")

        #get sql and download sql from sql format service
        sql, download_sql = QueryConstructorService.format_glad_sql(conf, from_year, from_date, to_year, to_date, iso, state, dist)

        data = AnalysisService.make_glad_request(sql, geostore)

        if agg_values:
            agg_data = QueryConstructorService.aggregate_glad_values(data, conf, from_year, from_date, to_year, to_date, geostore, download_sql)
            standard_format = ResponseService.standardize_response('Glad', agg_data, "COUNT(julian_day)", datasetID, download_sql=download_sql, area=area, geostore=geostore, agg=True)
        else:
            standard_format = ResponseService.standardize_response('Glad', data, "COUNT(julian_day)", datasetID, download_sql, area, geostore)

    elif request.method == 'POST':
        #get paramters from payload
        period = request.get_json().get('period', None) if request.get_json() else None
        conf = request.get_json().get('gladConfirmOnly', None) if request.get_json() else None

        #format period request to julian dates
        from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period=period, datasetID=datasetID, indexID=indexID, value="julian_day")

        #get sql and download sql from sql format service
        sql = QueryConstructorService.format_glad_sql(conf, from_year, from_date, to_year, to_date, iso, state, dist)

        data = AnalysisService.make_glad_request_post(sql, geojson)
        standard_format = ResponseService.standardize_response('Glad', data, "COUNT(julian_day)", datasetID)

    return jsonify({'data': standard_format}), 200

"""GLAD ENDPOINTS"""

@endpoints.route('/glad-alerts', methods=['GET', 'POST'])
@validate_glad_period
@validate_geostore

def query_glad():
    """analyze glad by geostore or geojson"""

    if request.method == 'GET':
        logging.info('[ROUTER]: get glad by geosotre')

        geostore = request.args.get('geostore', None)

        #make request to geostore to get area in hectares
        area = GeostoreService.make_area_request(geostore)

        return analyze(area=area, geostore=geostore)

    elif request.method == 'POST':
        logging.info('[ROUTER]: post geojson to glad')

        geojson = request.get_json().get('geojson', None) if request.get_json() else None

        return analyze(geojson=geojson)

    else:
        return error(status=405, detail="Operation not supported")

@endpoints.route('/glad-alerts/admin/<iso_code>', methods=['GET'])
@validate_glad_period
@validate_admin

def glad_country(iso_code):
    """analyze glad by gadm geom"""
    logging.info('[ROUTER]: Running country level glad analysis')

    #get area in hectares from geostore
    area = GeostoreService.make_gadm_request(iso_code)

    #analyze layer
    return analyze(area=area, iso=iso_code)

@endpoints.route('/glad-alerts/admin/<iso_code>/<admin_id>', methods=['GET'])
@validate_glad_period
@validate_admin

def glad_admin(iso_code, admin_id):
    """analyze glad by gadm geom"""
    logging.info('[ROUTER]: Running state level glad analysis')

    #get area in hectares from geostore
    area = GeostoreService.make_gadm_request(iso_code, admin_id)

    #analyze
    return analyze(area=area, iso=iso_code, state=admin_id)


@endpoints.route('/glad-alerts/admin/<iso_code>/<admin_id>/<dist_id>', methods=['GET'])
@validate_glad_period
@validate_admin

def glad_dist(iso_code, admin_id, dist_id):
    """analyze glad by gadm geom"""
    logging.info('[ROUTER]: Running district level glad analysis')

    #get area in hectares from geostore
    area = GeostoreService.make_gadm_request(iso_code, admin_id, dist_id)

    #send query to glad elastic databse through analysis service
    return analyze(area=area, iso=iso_code, state=admin_id, dist=dist_id)

@endpoints.route('/glad-alerts/use/<use_type>/<use_id>', methods=['GET'])
@validate_use
@validate_glad_period

def glad_use(use_type, use_id):
    """analyze glad by land use geom"""
    logging.info('[ROUTER]: Intersecting GLAD with Land Use data')

    #get geostore ID and area in hectares from geostore
    geostore, area = GeostoreService.make_use_request(use_type, use_id)

    return analyze(area=area, geostore=geostore)

@endpoints.route('/glad-alerts/wdpa/<wdpa_id>', methods=['GET'])
@validate_glad_period
@validate_wdpa

def glad_wdpa(wdpa_id):
    """analyze glad by wdpa geom"""
    logging.info('[ROUTER]: QUERY GLAD BY WDPA DATA')

    #Get geostore ID and area in hectares from geostore
    geostore, area = GeostoreService.make_wdpa_request(wdpa_id)

    return analyze(area=area, geostore=geostore)

@endpoints.route('/glad-alerts/date-range', methods=['GET'])
def glad_date_range():
    """get glad date range"""
    logging.info('[ROUTER]: Creating Glad Date Range')

    #set dataset ID
    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    indexID = '{}'.format(os.getenv('GLAD_INDEX_ID'))

    #get min and max date from sql queries
    min_year, min_julian, max_year, max_julian = DateService.get_min_max_date('julian_day', datasetID, indexID)
    min_date, max_date = DateService.format_date_sql(min_year, min_julian, max_year, max_julian)

    #standardize date response
    response = ResponseService.format_date_range("Glad", min_date, max_date)

    return jsonify({'data': response}), 200

@endpoints.route('/glad-alerts/latest', methods=['GET'])
def glad_latest():
    """get glad latest date"""
    logging.info('[ROUTER]: Getting latest date')

    #set dataset ID
    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    indexID = '{}'.format(os.getenv('GLAD_INDEX_ID'))

    #get max date
    min_year, min_julian, max_year, max_julian = DateService.get_min_max_date('julian_day', datasetID, indexID)
    max_date = DateService.format_date_sql(min_year, min_julian, max_year, max_julian)[1]

    #standardize latest date response
    response = ResponseService.format_latest_date("Glad", max_date)

    return jsonify({'data': response}), 200

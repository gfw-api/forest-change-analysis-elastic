import os
import logging
import datetime

from flask import jsonify, request

from . import endpoints
from gladanalysis.services import GeostoreService, DateService, QueryConstructorService, AnalysisService, ResponseService, SummaryService
from gladanalysis.errors import GeostoreNotFound
from gladanalysis.routes.api.v2 import error
from gladanalysis.validators import validate_geostore, validate_glad_period, validate_agg, validate_admin, validate_use, validate_wdpa

datasetID = os.getenv('GLAD_DATASET_ID')
indexID = os.getenv('GLAD_INDEX_ID')

def analyze(area=None, geostore=None, iso=None, state=None, dist=None, geojson=None):
    """Analyze method to execute queries
    This is designed to format the dates of the request, create the sql and download sql queries from
    the dates, retrieve the data from the queries and send the data to a formatter service to format
    the API response.
    :param area: the area of the request retrieved by the geostore
    :param geostore: the geostore id of the request
    :param iso: the country iso if specified
    :param dist: the district ID based on gadm
    :param state: the state ID based on gadm
    :param geojson: the geojson inlcuded in the body (if post request)
    :return: returns the response of the API request formatted by the format service"""

    today = datetime.datetime.today().strftime('%Y-%m-%d')

    #get parameters from query string
    period = request.args.get('period', '2015-01-01,{}'.format(today))
    conf = request.args.get('gladConfirmOnly', False)
    agg_values = request.args.get('aggregate_values', False)
    agg_by = request.args.get('aggregate_by', None)

    # grab geojson if it exists
    geojson = request.get_json().get('geojson', None) if request.get_json() else None

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period=period, datasetID=datasetID, indexID=indexID, value="julian_day")

    sql, download_sql = QueryConstructorService.format_glad_sql(conf, from_year, from_date, to_year, to_date, iso, state, dist, agg_values)

    kwargs = {'download_sql': download_sql,
              'area': area,
              'geostore': geostore,
              'agg': agg_values,
              'period': period,
              'conf': conf}

    if agg_values:
        if not agg_by or agg_by == 'day':
            agg_by = 'julian_day'

        # add agg_by to kwargs
        kwargs['agg_by'] = agg_by

        data = AnalysisService.make_analysis_request(datasetID, sql, geostore, geojson)
        agg_data = SummaryService.create_time_table('glad', data, agg_by)
        standard_format = ResponseService.standardize_response('Glad', agg_data, datasetID, **kwargs)

    else:
        kwargs['agg_by'] = None
        kwargs['count'] = "COUNT(julian_day)"
        data = AnalysisService.make_analysis_request(datasetID, sql, geostore, geojson)
        standard_format = ResponseService.standardize_response('Glad', data, datasetID, **kwargs)

    return jsonify({'data': standard_format}), 200


"""GLAD ENDPOINTS"""
@endpoints.route('/glad-alerts', methods=['GET', 'POST'])
@validate_glad_period
@validate_geostore
@validate_agg

def query_glad():
    """analyze glad by geostore or geojson"""

    if request.method == 'GET':
        logging.info('[ROUTER]: get glad by geostore')

        geostore = request.args.get('geostore', None)

        #make request to geostore to get area in hectares
        try:
            area = GeostoreService.make_area_request(geostore)
        except GeostoreNotFound:
            logging.error('[ROUTER]: Geostore Not Found')
            return error(status=404, detail='Geostore not found')

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

    #get max date
    min_year, min_julian, max_year, max_julian = DateService.get_min_max_date('julian_day', datasetID, indexID)
    max_date = DateService.format_date_sql(min_year, min_julian, max_year, max_julian)[1]

    #standardize latest date response
    response = ResponseService.format_latest_date("Glad", max_date)

    return jsonify({'data': response}), 200

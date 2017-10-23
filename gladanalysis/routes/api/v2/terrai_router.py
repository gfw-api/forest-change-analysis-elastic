import os
import logging
import datetime

from flask import jsonify, request

from . import endpoints
from gladanalysis.services import GeostoreService, DateService, QueryConstructorService, AnalysisService, ResponseService, SummaryService
from gladanalysis.errors import GeostoreNotFound
from gladanalysis.routes.api.v2 import error
from gladanalysis.validators import validate_geostore, validate_terrai_period, validate_agg, validate_admin, validate_use, validate_wdpa

datasetID = os.getenv('TERRAI_DATASET_ID')
indexID = os.getenv('TERRAI_INDEX_ID')

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

    #get parameter from query string
    period = request.args.get('period', '2004-01-01,{}'.format(today))
    agg_values = request.args.get('aggregate_values', False)
    agg_by = request.args.get('aggregate_by', None)

    # grab geojson if it exists
    geojson = request.get_json().get('geojson', None) if request.get_json() else None

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period, datasetID, indexID, "day")

    #grab query and download sql from sql service
    sql, download_sql = QueryConstructorService.format_terrai_sql(from_year, from_date, to_year, to_date, iso, state, dist, agg_values)

    kwargs = {'download_sql': download_sql,
              'area': area,
              'geostore': geostore,
              'agg': agg_values,
              'period': period}

    if agg_values:
        if not agg_by or agg_by == 'julian_day':
            agg_by = 'day'

        kwargs['agg_by'] = agg_by

        data = AnalysisService.make_analysis_request(datasetID, sql, geostore, geojson)
        agg_data = SummaryService.create_time_table('terrai', data, agg_by)
        standard_format = ResponseService.standardize_response('Terrai', agg_data, datasetID, **kwargs)

    else:
        kwargs['agg_by'] = None
        kwargs['count'] = "COUNT(julian_day)"
        data = AnalysisService.make_analysis_request(datasetID, sql, geostore, geojson)
        standard_format = ResponseService.standardize_response('Terrai', data, datasetID, **kwargs)

    return jsonify({'data': standard_format}), 200

"""TERRA I ENDPOINTS"""

@endpoints.route('/terrai-alerts', methods=['GET', 'POST'])
@validate_terrai_period
@validate_geostore
@validate_agg

def query_terrai():
    """analyze terrai by geostore or geojson"""

    if request.method == 'GET':
        logging.info('[ROUTER]: get Terra I by Geostore')

        geostore = request.args.get('geostore', None)

        #get area of request in hectares from geostore
        try:
            area = GeostoreService.make_area_request(geostore)
        except GeostoreNotFound:
            logging.error('[ROUTER]: Geostore Not Found')
            return error(status=404, detail='Geostore not found')

        return analyze(area=area, geostore=geostore)

    elif request.method == 'POST':
        logging.info('[ROUTER]: post geojson to terrai')

        geojson = request.get_json().get('geojson', None) if request.get_json() else None

        return analyze(geojson=geojson)

    else:
        return error(status=405, detail="Operation not supported")

@endpoints.route('/terrai-alerts/admin/<iso_code>', methods=['GET'])
@validate_terrai_period
@validate_admin

def terrai_country(iso_code):
    """analyze terrai by gadm"""
    logging.info('Running Terra I country analysis')

    #get area in hectares of response from geostore
    area = GeostoreService.make_gadm_request(iso_code)

    return analyze(area, iso=iso_code)

@endpoints.route('/terrai-alerts/admin/<iso_code>/<admin_id>', methods=['GET'])
@validate_terrai_period
@validate_admin

def terrai_admin(iso_code, admin_id):
    """analyze terrai by gadm"""
    logging.info('Running Terra I state analysis')

    #get area in hectares of request from geostore
    area = GeostoreService.make_gadm_request(iso_code, admin_id)

    return analyze(area, iso=iso_code, state=admin_id)

@endpoints.route('/terrai-alerts/admin/<iso_code>/<admin_id>/<dist_id>', methods=['GET'])
@validate_terrai_period
@validate_admin

def terrai_dist(iso_code, admin_id, dist_id):
    """analyze terrai by gadm"""
    logging.info('Running Terra I Analysis on District')

    #get area in hectares of request from geostore
    area = GeostoreService.make_gadm_request(iso_code, admin_id, dist_id)

    return analyze(area, iso=iso_code, state=admin_id, dist=dist_id)

@endpoints.route('/terrai-alerts/use/<use_type>/<use_id>', methods=['GET'])
@validate_use
@validate_terrai_period

def terrai_use(use_type, use_id):
    """analyze terrai by land use"""
    logging.info('Intersect Terra I and Land Use data')

    #get geostore ID and area in hectares of request from geostore
    geostore, area = GeostoreService.make_use_request(use_type, use_id)

    return analyze(area, geostore)

@endpoints.route('/terrai-alerts/wdpa/<wdpa_id>', methods=['GET'])
@validate_terrai_period
@validate_wdpa

def terrai_wdpa(wdpa_id):
    """analyze terrai by wdpa geom"""
    logging.info('Intersect Terra I and WDPA')

    #get geostore id and area in hectares of request from geostore
    geostore, area = GeostoreService.make_wdpa_request(wdpa_id)

    return analyze(area, geostore)

@endpoints.route('/terrai-alerts/date-range', methods=['GET'])
def terrai_date_range():
    """get terrai date range"""
    logging.info('Creating Terra I Date Range')

    #get min and max date from sql queries
    min_year, min_julian, max_year, max_julian = DateService.get_min_max_date('day', datasetID, indexID)
    min_date, max_date = DateService.format_date_sql(min_year, min_julian, max_year, max_julian)

    #standardize response
    response = ResponseService.format_date_range("Terrai", min_date, max_date)

    return jsonify({'data': response}), 200

@endpoints.route('/terrai-alerts/latest', methods=['GET'])
def terrai_latest():
    """get TerraI latest date"""
    logging.info('Getting latest date')

    #get max date
    min_year, min_julian, max_year, max_julian = DateService.get_min_max_date('day', datasetID, indexID)
    max_date = DateService.format_date_sql(min_year, min_julian, max_year, max_julian)[1]

    #standardize latest date response
    response = ResponseService.format_latest_date("Terrai", max_date)

    return jsonify({'data': response}), 200

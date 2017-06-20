import os
import logging
import datetime

from flask import jsonify, request

from . import endpoints
from gladanalysis.services import GeostoreService
from gladanalysis.services import DateService
from gladanalysis.services import SqlService
from gladanalysis.services import AnalysisService
from gladanalysis.services import ResponseService
from gladanalysis.responders import ErrorResponder
from gladanalysis.validators import validate_geostore, validate_terrai_period, validate_admin, validate_use, validate_wdpa

def analyze(area, geostore=None, iso=None, state=None, dist=None):
    """analyze method to execute Queries"""

    period = request.args.get('period', None)

    if not period:
        period = None

    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    indexID = '{}'.format(os.getenv('TERRAI_INDEX_ID'))

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period, datasetID, indexID)

    #grab query and download sql from sql service
    sql, download_sql = SqlService.format_terrai_sql(from_year, from_date, to_year, to_date, iso, state, dist)

    #send query to terra i elastic database
    data = AnalysisService.make_terrai_request(sql, geostore)

    standard_format = ResponseService.standardize_response('Terrai', data, "COUNT(day)", datasetID, download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

"""TERRA I ENDPOINTS"""

@endpoints.route('/terrai-alerts', methods=['GET'])
@validate_geostore
@validate_terrai_period

def query_terrai():
    """analyze terrai by geostore"""
    logging.info('Query Terra I by Geostore')

    geostore = request.args.get('geostore', None)

    #get area of request in hectares from geostore
    area = GeostoreService.make_area_request(geostore)

    return analyze(area, geostore)

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

    #set dataset ids
    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    indexID = '{}'.format(os.getenv('TERRAI_INDEX_ID'))

    #get min and max date from sql queries
    min_year, min_julian, max_year, max_julian = DateService.get_min_max_date(datasetID, indexID)
    min_date, max_date = DateService.format_date_sql(min_year, min_julian, max_year, max_julian)

    #standardize response
    response = ResponseService.format_date_range("Terrai", min_date, max_date)

    return jsonify({'data': response}), 200

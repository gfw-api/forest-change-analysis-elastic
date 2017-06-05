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
from gladanalysis.validators import validate_geostore, validate_glad_period, validate_terrai_period, validate_admin, validate_use, validate_wdpa

"""GLAD ENDPOINTS"""

@endpoints.route('/glad-alerts', methods=['GET'])
@validate_geostore
@validate_glad_period

def query_glad():
    """Query GLAD"""
    logging.info('QUERYING GLAD')

    geostore = request.args.get('geostore', None)
    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #get sql and download sql from sql format service
    sql, download_sql = SqlService.format_glad_sql(conf, from_year, from_date, to_year, to_date)

    #send sql and geostore to analysis service to query elastic database
    data = AnalysisService.make_glad_request(sql, geostore)

    #make request to geostore to get area in hectares
    area = GeostoreService.make_area_request(geostore)

    #standardize response
    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    standard_format = ResponseService.standardize_response('Glad', data, "COUNT(julian_day)", datasetID, download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/glad-alerts/admin/<iso_code>', methods=['GET'])
@validate_glad_period
@validate_admin

def glad_country(iso_code):

    logging.info('Running country level glad analysis')

    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #get query and download sql from sql format service
    sql, download_sql = SqlService.format_glad_sql(conf, from_year, from_date, to_year, to_date, iso_code)

    #get area in hectares from geostore
    area_ha = GeostoreService.make_gadm_request(iso_code)

    #make analysis request to the GLAD elastic database
    data = AnalysisService.make_glad_request(sql)

    #standardize response from analysis service
    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    standard_format = ResponseService.standardize_response('Glad', data, "COUNT(julian_day)", datasetID, download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/glad-alerts/admin/<iso_code>/<admin_id>', methods=['GET'])
@validate_glad_period
@validate_admin

def glad_admin(iso_code, admin_id):

    logging.info('Running state level glad analysis')

    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #get query and download sql from sql format service
    sql, download_sql = SqlService.format_glad_sql(conf, from_year, from_date, to_year, to_date, iso_code, admin_id)

    #get area in hectares from geostore
    area_ha = GeostoreService.make_gadm_request(iso_code, admin_id)

    #send query to GLAD elastic database through analysis service
    data = AnalysisService.make_glad_request(sql)

    #standardize response
    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    standard_format = ResponseService.standardize_response('Glad', data, "COUNT(julian_day)", datasetID, download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/glad-alerts/admin/<iso_code>/<admin_id>/<dist_id>', methods=['GET'])
@validate_glad_period
@validate_admin

def glad_dist(iso_code, admin_id, dist_id):

    logging.info('Running district level glad analysis')

    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #get query and download sql from sql format service
    sql, download_sql = SqlService.format_glad_sql(conf, from_year, from_date, to_year, to_date, iso_code, admin_id, dist_id)

    #get area in hectares from geostore
    area_ha = GeostoreService.make_gadm_request(iso_code, admin_id)

    #send query to glad elastic databse through analysis service
    data = AnalysisService.make_glad_request(sql)

    #standardize response
    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    standard_format = ResponseService.standardize_response('Glad', data, "COUNT(julian_day)", datasetID, download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/glad-alerts/use/<use_type>/<use_id>', methods=['GET'])
@validate_use
@validate_glad_period

def glad_use(use_type, use_id):

    logging.info('Intersecting GLAD with Land Use data')

    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #get query and download sql from sql format service
    sql, download_sql = SqlService.format_glad_sql(conf, from_year, from_date, to_year, to_date)

    #get geostore ID and area in hectares from geostore
    geostore, area = GeostoreService.make_use_request(use_type, use_id)

    #send query to Glad elastic database through analysis service
    data = AnalysisService.make_glad_request(sql, geostore)

    #standardize response
    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    standard_format = ResponseService.standardize_response('Glad', data, "COUNT(julian_day)", datasetID, download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/glad-alerts/wdpa/<wdpa_id>', methods=['GET'])
@validate_glad_period
@validate_wdpa

def glad_wdpa(wdpa_id):

    logging.info('QUERY GLAD BY WDPA DATA')

    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #get query and download sql from sql format service
    sql, download_sql = SqlService.format_glad_sql(conf, from_year, from_date, to_year, to_date)

    #Get geostore ID and area in hectares from geostore
    geostore, area = GeostoreService.make_wdpa_request(wdpa_id)

    #send query to Glad elastic database through analysis service
    data = AnalysisService.make_glad_request(sql, geostore)

    #Standardize response
    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))
    standard_format = ResponseService.standardize_response('Glad', data, "COUNT(julian_day)", datasetID, download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/glad-alerts/date-range', methods=['GET'])
def glad_date_range():

    logging.info('Creating Glad Date Range')

    #set dataset ID
    datasetID = '{}'.format(os.getenv('GLAD_DATASET_ID'))

    #Get max year from database
    max_year_sql = '?sql=select MAX(year)from {}'.format(os.getenv('GLAD_INDEX_ID'))
    max_year = DateService.get_date(datasetID, max_year_sql, 'MAX(year)')

    #Get max julian date from database
    max_sql = '?sql=select MAX(julian_day)from {} where year = {}'.format(os.getenv('GLAD_INDEX_ID'), max_year)
    max_julian = DateService.get_date(datasetID, max_sql, 'MAX(julian_day)')

    #Set min and max julian values (min value shouldn't change, hence hard-code)
    latest_year, latest_month, latest_day = DateService.julian_day_to_date(max_year, max_julian)

    #format day
    max_date = '%s-%02d-%s' %(latest_year, latest_month, latest_day)
    min_date = '2015-01-01'

    #standardize date response
    response = ResponseService.format_date_range("Glad", min_date, max_date)

    return jsonify({'data': response}), 200

"""TERRA I ENDPOINTS"""
@endpoints.route('/terrai-alerts', methods=['GET'])
@validate_geostore
@validate_terrai_period

def query_terrai():

    logging.info('Query Terra I by Geostore')

    geostore = request.args.get('geostore', None)
    period = request.args.get('period', None)

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #grab query and download sql from sql service
    sql, download_sql = SqlService.format_terrai_sql(from_year, from_date, to_year, to_date)

    #send query to terra i elastic database
    data = AnalysisService.make_terrai_request(sql, geostore)

    #get area of request in hectares from geostore
    area = GeostoreService.make_area_request(geostore)

    #standardize response
    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    standard_format = ResponseService.standardize_response('Terrai', data, "COUNT(day)", datasetID, download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terrai-alerts/admin/<iso_code>', methods=['GET'])
@validate_terrai_period
@validate_admin

def terrai_country(iso_code):

    logging.info('Running Terra I country analysis')

    period = request.args.get('period', None)

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #get query and download sql from sql format service
    sql, download_sql = SqlService.format_terrai_sql(from_year, from_date, to_year, to_date, iso_code)

    #get area in hectares of response from geostore
    area_ha = GeostoreService.make_gadm_request(iso_code)

    #send query to terra i elastic database
    data = AnalysisService.make_terrai_request(sql)

    #standardize response
    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    standard_format = ResponseService.standardize_response('Terrai', data, "COUNT(day)", datasetID, download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terrai-alerts/admin/<iso_code>/<admin_id>', methods=['GET'])
@validate_terrai_period
@validate_admin

def terrai_admin(iso_code, admin_id):
    logging.info('Running Terra I state analysis')

    period = request.args.get('period', None)

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #get query and download sql from sql format service
    sql, download_sql = SqlService.format_terrai_sql(from_year, from_date, to_year, to_date, iso_code, admin_id)

    #get area in hectares of request from geostore
    area_ha = GeostoreService.make_gadm_request(iso_code, admin_id)

    #send query to terra i elastic database through analysis service
    data = AnalysisService.make_terrai_request(sql)

    #standardize response
    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    standard_format = ResponseService.standardize_response('Terrai', data, "COUNT(day)", datasetID, download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terrai-alerts/admin/<iso_code>/<admin_id>/<dist_id>', methods=['GET'])
@validate_terrai_period
@validate_admin

def terrai_dist(iso_code, admin_id, dist_id):
    logging.info('Running Terra I Analysis on District')

    period = request.args.get('period', None)

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #get query and download sql from sql format service
    sql, download_sql = SqlService.format_terrai_sql(from_year, from_date, to_year, to_date, iso_code, admin_id, dist_id)

    #get area in hectares of request from geostore
    area_ha = GeostoreService.make_gadm_request(iso_code, admin_id, dist_id)

    #send query to terra i elastic database through analysis service
    data = AnalysisService.make_terrai_request(sql)

    #standardize response
    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    standard_format = ResponseService.standardize_response('Terrai', data, "COUNT(day)", datasetID, download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terrai-alerts/use/<use_type>/<use_id>', methods=['GET'])
@validate_use
@validate_terrai_period

def terrai_use(use_type, use_id):

    logging.info('Intersect Terra I and Land Use data')

    period = request.args.get('period', None)

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #get query and download sql from sql format service
    sql, download_sql = SqlService.format_terrai_sql(from_year, from_date, to_year, to_date)

    #get geostore ID and area in hectares of request from geostore
    geostore, area = GeostoreService.make_use_request(use_type, use_id)

    #send query to terra i elastic database through analysis service
    data = AnalysisService.make_terrai_request(sql, geostore)

    #standardize response
    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    standard_format = ResponseService.standardize_response('Terrai', data, "COUNT(day)", datasetID, download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terrai-alerts/wdpa/<wdpa_id>', methods=['GET'])
@validate_terrai_period
@validate_wdpa

def terrai_wdpa(wdpa_id):

    logging.info('Intersect Terra I and WDPA')

    period = request.args.get('period', None)

    #format period request to julian dates
    from_year, from_date, to_year, to_date = DateService.date_to_julian_day(period)

    #get query and download sql from sql format service
    sql, download_sql = SqlService.format_terrai_sql(from_year, from_date, to_year, to_date)

    #get geostore id and area in hectares of request from geostore
    geostore, area = GeostoreService.make_wdpa_request(wdpa_id)

    #Send query to Terra I elastic database through analysis service
    data = AnalysisService.make_terrai_request(sql, geostore)

    #standardize response
    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))
    standard_format = ResponseService.standardize_response('Terrai', data, "COUNT(day)", datasetID, download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terrai-alerts/date-range', methods=['GET'])
def terrai_date_range():

    logging.info('Creating Terra I Date Range')

    #SET DATASET ID
    datasetID = '{}'.format(os.getenv('TERRAI_DATASET_ID'))

    #Get max year from database
    max_year_sql = '?sql=select MAX(year)from {}'.format(os.getenv('TERRAI_INDEX_ID'))
    max_year = DateService.get_date(datasetID, max_year_sql, 'MAX(year)')

    #GET julian dates
    max_sql = '?sql=select MAX(day)from {} where year = {}'.format(os.getenv('TERRAI_INDEX_ID'), max_year)
    max_julian = DateService.get_date(datasetID, max_sql, 'MAX(day)')

    #convert julian to date
    latest_year, latest_month, latest_day = DateService.julian_day_to_date(max_year, max_julian)

    #format dates
    max_date = '%s-%02d-%s' %(latest_year, latest_month, latest_day)
    min_date = '2004-01-01'

    #standardize response
    response = ResponseService.format_date_range("Terrai", min_date, max_date)

    return jsonify({'data': response}), 200

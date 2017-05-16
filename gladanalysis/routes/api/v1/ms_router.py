import os
import logging
import datetime

from flask import jsonify, request
import requests

from . import endpoints
from gladanalysis.responders import ErrorResponder
from gladanalysis.utils.http import request_to_microservice

#comments: can probs put sql calls in a single function

def date_to_julian_day(input_date):
    #Helper function to transform dates

    try:
        date_obj = datetime.datetime.strptime(input_date, '%Y-%m-%d')
        time_tuple = date_obj.timetuple()
        logging.info(time_tuple.tm_year)
        return str(time_tuple.tm_year), str(time_tuple.tm_yday)

    except ValueError:
        return None, None

def format_glad_sql(from_year, from_date, to_year, to_date, iso=None, state=None, dist=None):

    select_sql = 'SELECT lat, long, confidence_text, year, julian_day '
    count_sql = 'SELECT count(julian_day) '
    from_sql = 'FROM index_e663eb0904de4f39b87135c6c2ed10b5 '
    order_sql = 'ORDER BY year, julian_day'

    if (int(from_year) < 2015 or int(to_year) > 2017):
        return jsonify({'errors': [{
            'status': '400',
            'title': 'GLAD period must be between 2015 and 2017'
            }]
        }), 400

    elif (from_year == '2015') and (to_year == '2017'):
        where_template = ("WHERE ((year = '2015' and julian_day >= {d1}) or "
        "(year = '2016') or "
        "(year = '2017' and julian_day <= {d2}))")

    elif from_year == to_year:
        where_template = 'WHERE ((year = {Y1} and julian_day >= {d1} and julian_day <= {d2}))'

    else:
        where_template = 'WHERE ((year = {y1} and julian_day >= {d1}) or (year = {y2} and julian_day <= {d2}))'

    geog_id_list = ['country_iso', 'state_id', 'dist_id']
    geog_val_list = [iso, state, dist]

    for geog_name, geog_value in zip(geog_id_list, geog_val_list):
        if geog_value:
            if geog_name == 'country_iso':
                where_template += " AND ({} = '{}')".format(geog_name, geog_value)
            else:
                where_template += ' AND ({} = {})'.format(geog_name, geog_value)

    where_sql = where_template.format(y1=from_year, d1=from_date, y2=to_year, d2=to_date)

    sql = '?sql=' + ''.join([count_sql, from_sql, where_sql])
    download_sql = '?sql=' + ''.join([select_sql, from_sql, where_sql, order_sql])

    return sql, download_sql

def format_terrai_sql(from_year, from_date, to_year, to_date, iso=None, state=None, dist=None):

    select_sql = 'SELECT lat, long, year, day '
    count_sql = 'SELECT count(day) '
    from_sql = 'FROM index_67cf7c0373654a1f8401d42c3706b7de '
    order_sql = 'ORDER BY year, day'


    if (int(from_year) < 2004 or int(to_year) > 2017):
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Terra I period must be between 2004 and 2017'
            }]
        }), 400

    else:
        where_template = 'WHERE ((year = {y1} and day >= {d1}) or (year >= int({y1} + 1) and year <= {y2}) or (year = {y2} and day <= {d2}))'

    geog_id_list = ['country_iso', 'state_id', 'dist_id']
    geog_val_list = [iso, state, dist]

    for geog_name, geog_value in zip(geog_id_list, geog_val_list):
        if geog_value:
            if geog_name == 'country_iso':
                where_template += " AND ({} = '{}')".format(geog_name, geog_value)
            else:
                where_template += ' AND ({} = {})'.format(geog_name, geog_value)

    where_sql = where_template.format(y1=from_year, d1=from_date, y2=to_year, d2=to_date)

    sql = '?sql=' + ''.join([count_sql, from_sql, where_sql])
    download_sql = '?sql=' + ''.join([select_sql, from_sql, where_sql, order_sql])

    return sql, download_sql

def make_glad_request(sql, confidence, geostore=None):

    #format request to glad dataset
    url = 'http://staging-api.globalforestwatch.org/query/'
    datasetID = '274b4818-be18-4890-9d10-eae56d2a82e5'
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
    datasetID = '67cf7c03-7365-4a1f-8401-d42c3706b7de'
    f = '&format=json'

    if geostore:
        full = url + datasetID + sql + "&geostore=" + geostore + f
    else:
        full = url + datasetID + sql + f

    r = requests.get(url=full)
    data = r.json()
    return data

def make_area_request(geostore):

    area_url = 'http://staging-api.globalforestwatch.org/geostore/' + geostore
    r_area = requests.get(url=area_url)
    area_resp = r_area.json()
    area = area_resp['data']['attributes']['areaHa']
    return area

def make_gadm_request(iso_code, admin_id):

    geostore_url = 'https://staging-api.globalforestwatch.org/geostore/admin/%s/%s'%(iso_code, admin_id)
    r = requests.get(url=geostore_url)
    geostore_data = r.json()
    geostore = geostore_data['data']['id']
    area_ha = geostore_data['data']['attributes']['areaHa']
    return (geostore, area_ha)

def make_country_request(iso_code):

    geostore_url = 'https://staging-api.globalforestwatch.org/geostore/admin/%s'%(iso_code)
    r = requests.get(url=geostore_url)
    geostore_data = r.json()
    geostore = geostore_data['data']['id']
    area_ha = geostore_data['data']['attributes']['areaHa']
    return (geostore, area_ha)

def make_use_request(use_type, use_id):

    area_url = 'http://staging-api.globalforestwatch.org/geostore/use/%s/%s' %(use_type, use_id)
    r = requests.get(url=area_url)
    geostore_data = r.json()
    geostore = geostore_data['data']['id']
    area = geostore_data['data']['attributes']['areaHa']
    return (geostore, area)

def make_wdpa_request(wdpa_id):

    area_url = 'http://staging-api.globalforestwatch.org/geostore/wdpa/%s' %(wdpa_id)
    r = requests.get(url=area_url)
    geostore_data = r.json()
    geostore = geostore_data['data']['id']
    area = geostore_data['data']['attributes']['areaHa']
    return (geostore, area)

def get_date(datasetID, sql, value):

    url = 'http://staging-api.globalforestwatch.org/query/'
    f = '&format=json'

    full = url + datasetID + sql + f
    r = requests.get(url=full)
    values = r.json()
    date_value = values['data'][0][value]
    return date_value

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
def query_glad():
    """Query GLAD"""
    logging.info('QUERYING GLAD')

    geostore = request.args.get('geostore', None)
    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    if not geostore or not period:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'geostore and period should be set'
            }]
        }), 400

    if len(period.split(',')) < 2:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Period needs 2 arguments'
            }]
        }), 400

    period_from = period.split(',')[0]
    period_to = period.split(',')[1]

    from_year, from_date = date_to_julian_day(period_from)
    to_year, to_date = date_to_julian_day(period_to)

    if None in (from_year, to_year):
        return jsonify({'errors': [{
                'status': '400',
                'title': 'Invalid period supplied; must be YYYY-MM-DD,YYYY-MM-DD'
                }]
            }), 400

    #send to sql formatter function
    sql, download_sql = format_glad_sql(from_year, from_date, to_year, to_date)

    #create condition to look for confidence filter
    if conf == 'true' or conf == 'True':
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    #query glad database
    data = make_glad_request(sql, confidence, geostore)

    #make request to geostore to get area in hectares
    area = make_area_request(geostore)

    #standardize response
    standard_format = standardize_response(data, "COUNT(julian_day)", '274b4818-be18-4890-9d10-eae56d2a82e5', download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200


@endpoints.route('/terraianalysis', methods=['GET'])
def query_terrai():

    logging.info('QUERYING TERRA I')

    geostore = request.args.get('geostore', None)
    period = request.args.get('period', None)

    if not geostore or not period:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'geostore and period should be set'
            }]
        }), 400

    if len(period.split(',')) < 2:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Period needs 2 arguments'
            }]
        }), 400

    period_from = period.split(',')[0]
    period_to = period.split(',')[1]

    from_year, from_date = date_to_julian_day(period_from)
    to_year, to_date = date_to_julian_day(period_to)

    if None in (from_year, to_year):
        return jsonify({'errors': [{
                'status': '400',
                'title': 'Invalid period supplied; must be YYYY-MM-DD,YYYY-MM-DD'
                }]
            }), 400

    #create conditions that issue correct sql
    sql, download_sql = format_terrai_sql(from_year, from_date, to_year, to_date)

    #format request parameters to Terra I
    data = make_terrai_request(sql, geostore)

    #get area from geostore
    area = make_area_request(geostore)

    standard_format = standardize_response(data, "COUNT(day)", '67cf7c03-7365-4a1f-8401-d42c3706b7de', download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/gladanalysis/admin/<iso_code>/<admin_id>/<dist_id>', methods=['GET'])
def glad_dist(iso_code, admin_id, dist_id):

    logging.info('Running GADM level glad analysis')

    #accept period parameter
    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    if not iso_code or not admin_id or not dist_id:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'ISO code, State ID and District ID should be set'
            }]
        }), 400

    #format date and format error responses
    if len(period.split(',')) < 2:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Period needs 2 arguments'
            }]
        }), 400

    period_from = period.split(',')[0]
    period_to = period.split(',')[1]

    from_year, from_date = date_to_julian_day(period_from)
    to_year, to_date = date_to_julian_day(period_to)

    if None in (from_year, to_year):
        return jsonify({'errors': [{
                'status': '400',
                'title': 'Invalid period supplied; must be YYYY-MM-DD,YYYY-MM-DD'
                }]
            }), 400

    #send to sql formatter function
    sql, download_sql = format_glad_sql(from_year, from_date, to_year, to_date, iso_code, admin_id, dist_id)

    #get geostore id from admin areas and total area of geostore request
    area_ha = make_gadm_request(iso_code, admin_id)[1]

    if conf == 'true' or conf == "True":
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    #query glad database
    data = make_glad_request(sql, confidence)

    standard_format = standardize_response(data, "COUNT(julian_day)", '274b4818-be18-4890-9d10-eae56d2a82e5', download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/gladanalysis/admin/<iso_code>/<admin_id>', methods=['GET'])
def glad_admin(iso_code, admin_id):

    logging.info('Running GADM level glad analysis')

    #accept period parameter
    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    if not iso_code or not admin_id:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'ISO code and State ID should be set'
            }]
        }), 400

    #format date and format error responses
    if len(period.split(',')) < 2:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Period needs 2 arguments'
            }]
        }), 400

    period_from = period.split(',')[0]
    period_to = period.split(',')[1]

    from_year, from_date = date_to_julian_day(period_from)
    to_year, to_date = date_to_julian_day(period_to)

    if None in (from_year, to_year):
        return jsonify({'errors': [{
                'status': '400',
                'title': 'Invalid period supplied; must be YYYY-MM-DD,YYYY-MM-DD'
                }]
            }), 400

    #send to sql formatter function
    sql, download_sql = format_glad_sql(from_year, from_date, to_year, to_date, iso_code, admin_id)

    #get geostore id from admin areas and total area of geostore request
    area_ha = make_gadm_request(iso_code, admin_id)[1]

    if conf == 'true' or conf == "True":
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    #query glad database
    data = make_glad_request(sql, confidence)

    standard_format = standardize_response(data, "COUNT(julian_day)", '274b4818-be18-4890-9d10-eae56d2a82e5', download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/gladanalysis/admin/<iso_code>', methods=['GET'])
def glad_country(iso_code):

    logging.info('Running country level glad analysis')

    #accept period parameter
    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    if not iso_code:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'ISO code should be set'
            }]
        }), 400

    #format date and format error responses
    if len(period.split(',')) < 2:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Period needs 2 arguments'
            }]
        }), 400

    period_from = period.split(',')[0]
    period_to = period.split(',')[1]

    from_year, from_date = date_to_julian_day(period_from)
    to_year, to_date = date_to_julian_day(period_to)

    if None in (from_year, to_year):
        return jsonify({'errors': [{
                'status': '400',
                'title': 'Invalid period supplied; must be YYYY-MM-DD,YYYY-MM-DD'
                }]
            }), 400

    #send to sql formatter function
    sql, download_sql = format_glad_sql(from_year, from_date, to_year, to_date, iso_code)

    #get geostore id from admin areas and total area of geostore request
    area_ha = make_country_request(iso_code)[1]

    if conf == 'true' or conf == "True":
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    #make request to glad database
    data = make_glad_request(sql, confidence)

    standard_format = standardize_response(data, "COUNT(julian_day)", '274b4818-be18-4890-9d10-eae56d2a82e5', download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terraianalysis/admin/<iso_code>/<admin_id>', methods=['GET'])
def terrai_admin(iso_code, admin_id):
    logging.info('QUERYING TERRA I AT GADM LEVEL')

    period = request.args.get('period', None)

    if not iso_code or not admin_id:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'ISO code and State ID should be set'
            }]
        }), 400


    if not period:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'time period should be set'
            }]
        }), 400

    if len(period.split(',')) < 2:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Period needs 2 arguments'
            }]
        }), 400

    period_from = period.split(',')[0]
    period_to = period.split(',')[1]

    from_year, from_date = date_to_julian_day(period_from)
    to_year, to_date = date_to_julian_day(period_to)

    if None in (from_year, to_year):
        return jsonify({'errors': [{
                'status': '400',
                'title': 'Invalid period supplied; must be YYYY-MM-DD,YYYY-MM-DD'
                }]
            }), 400

    #send dates to sql formatter
    sql, download_sql = format_terrai_sql(from_year, from_date, to_year, to_date, iso_code, admin_id)

    #get geostore id from admin areas and total area of geostore request
    # geostore = make_gadm_request(iso_code, admin_id)[0]
    area_ha = make_gadm_request(iso_code, admin_id)[1]

    #Make request to terra i dataset
    data = make_terrai_request(sql)

    standard_format = standardize_response(data, "COUNT(day)", '67cf7c03-7365-4a1f-8401-d42c3706b7de', download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terraianalysis/admin/<iso_code>/<admin_id>/<dist_id>', methods=['GET'])
def terrai_dist(iso_code, admin_id, dist_id):
    logging.info('QUERYING TERRA I AT GADM LEVEL')

    period = request.args.get('period', None)

    if not iso_code or not admin_id or not dist_id:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'ISO code, state ID and district ID should be set'
            }]
        }), 400


    if not period:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'time period should be set'
            }]
        }), 400

    if len(period.split(',')) < 2:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Period needs 2 arguments'
            }]
        }), 400

    period_from = period.split(',')[0]
    period_to = period.split(',')[1]

    from_year, from_date = date_to_julian_day(period_from)
    to_year, to_date = date_to_julian_day(period_to)

    if None in (from_year, to_year):
        return jsonify({'errors': [{
                'status': '400',
                'title': 'Invalid period supplied; must be YYYY-MM-DD,YYYY-MM-DD'
                }]
            }), 400

    #send dates to sql formatter
    sql, download_sql = format_terrai_sql(from_year, from_date, to_year, to_date, iso_code, admin_id, dist_id)

    #get area of request
    area_ha = make_gadm_request(iso_code, admin_id)[1]

    #Make request to terra i dataset
    data = make_terrai_request(sql)

    standard_format = standardize_response(data, "COUNT(day)", '67cf7c03-7365-4a1f-8401-d42c3706b7de', download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terraianalysis/admin/<iso_code>', methods=['GET'])
def terrai_country(iso_code):

    logging.info('QUERYING TERRA I AT COUNTRY LEVEL')

    period = request.args.get('period', None)

    if not iso_code:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'ISO code should be set'
            }]
        }), 400

    if not period:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'time period should be set'
            }]
        }), 400

    if len(period.split(',')) < 2:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Period needs 2 arguments'
            }]
        }), 400

    period_from = period.split(',')[0]
    period_to = period.split(',')[1]

    from_year, from_date = date_to_julian_day(period_from)
    to_year, to_date = date_to_julian_day(period_to)

    if None in (from_year, to_year):
        return jsonify({'errors': [{
                'status': '400',
                'title': 'Invalid period supplied; must be YYYY-MM-DD,YYYY-MM-DD'
                }]
            }), 400

    #send dates to sql formatter
    sql, download_sql = format_terrai_sql(from_year, from_date, to_year, to_date, iso_code)

    #get geostore id from admin areas and total area of geostore request
    # geostore = make_country_request(iso_code)[0]
    area_ha = make_country_request(iso_code)[1]

    #make request to terra i dataset
    data = make_terrai_request(sql)

    standard_format = standardize_response(data, "COUNT(day)", '67cf7c03-7365-4a1f-8401-d42c3706b7de', download_sql, area_ha)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/gladanalysis/use/<use_type>/<use_id>', methods=['GET'])
def glad_use(use_type, use_id):

    logging.info('QUERY GLAD BY LAND USE DATA')

    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    if not use_type or not use_id:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Use type and use ID should be set'
            }]
        }), 400

    if not period:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'time period should be set'
            }]
        }), 400

    if len(period.split(',')) < 2:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Period needs 2 arguments'
            }]
        }), 400

    period_from = period.split(',')[0]
    period_to = period.split(',')[1]

    from_year, from_date = date_to_julian_day(period_from)
    to_year, to_date = date_to_julian_day(period_to)

    if None in (from_year, to_year):
        return jsonify({'errors': [{
                'status': '400',
                'title': 'Invalid period supplied; must be YYYY-MM-DD,YYYY-MM-DD'
                }]
            }), 400

    #send to sql formatter function
    sql, download_sql = format_glad_sql(from_year, from_date, to_year, to_date)

    geostore = make_use_request(use_type, use_id)[0]
    area = make_use_request(use_type, use_id)[1]

    if conf == 'true' or conf == "True":
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    #make request to glad database
    data = make_glad_request(sql, confidence, geostore)

    standard_format = standardize_response(data, "COUNT(julian_day)", '274b4818-be18-4890-9d10-eae56d2a82e5', download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terraianalysis/use/<use_type>/<use_id>', methods=['GET'])
def terrai_use(use_type, use_id):

    logging.info('QUERY GLAD BY LAND USE DATA')

    period = request.args.get('period', None)

    if not use_type or not use_id:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Use type and use ID should be set'
            }]
        }), 400

    if not period:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'time period should be set'
            }]
        }), 400

    if len(period.split(',')) < 2:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Period needs 2 arguments'
            }]
        }), 400

    period_from = period.split(',')[0]
    period_to = period.split(',')[1]

    from_year, from_date = date_to_julian_day(period_from)
    to_year, to_date = date_to_julian_day(period_to)

    if None in (from_year, to_year):
        return jsonify({'errors': [{
                'status': '400',
                'title': 'Invalid period supplied; must be YYYY-MM-DD,YYYY-MM-DD'
                }]
            }), 400

    #send to sql formatter function
    sql, download_sql = format_terrai_sql(from_year, from_date, to_year, to_date)

    geostore = make_use_request(use_type, use_id)[0]
    area = make_use_request(use_type, use_id)[1]

    #make request to glad database
    data = make_terrai_request(sql, geostore)

    standard_format = standardize_response(data, "COUNT(day)", '67cf7c03-7365-4a1f-8401-d42c3706b7de', download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/gladanalysis/wdpa/<wdpa_id>', methods=['GET'])
def glad_wdpa(wdpa_id):

    logging.info('QUERY GLAD BY WDPA DATA')

    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

    if not wdpa_id:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'WDPA ID should be set'
            }]
        }), 400

    if not period:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'time period should be set'
            }]
        }), 400

    if len(period.split(',')) < 2:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Period needs 2 arguments'
            }]
        }), 400

    period_from = period.split(',')[0]
    period_to = period.split(',')[1]

    from_year, from_date = date_to_julian_day(period_from)
    to_year, to_date = date_to_julian_day(period_to)

    if None in (from_year, to_year):
        return jsonify({'errors': [{
                'status': '400',
                'title': 'Invalid period supplied; must be YYYY-MM-DD,YYYY-MM-DD'
                }]
            }), 400

    #send to sql formatter function
    sql, download_sql = format_glad_sql(from_year, from_date, to_year, to_date)

    geostore = make_wdpa_request(wdpa_id)[0]
    area = make_wdpa_request(wdpa_id)[1]

    if conf == 'true' or conf == "True":
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    #make request to glad database
    data = make_glad_request(sql, confidence, geostore)

    standard_format = standardize_response(data, "COUNT(julian_day)", '274b4818-be18-4890-9d10-eae56d2a82e5', download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/terraianalysis/wdpa/<wdpa_id>', methods=['GET'])
def terrai_wdpa(wdpa_id):

    logging.info('QUERY TERRA I BY WDPA')

    period = request.args.get('period', None)

    if not wdpa_id:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'WDPA should be set'
            }]
        }), 400

    if not period:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'time period should be set'
            }]
        }), 400

    if len(period.split(',')) < 2:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'Period needs 2 arguments'
            }]
        }), 400

    period_from = period.split(',')[0]
    period_to = period.split(',')[1]

    from_year, from_date = date_to_julian_day(period_from)
    to_year, to_date = date_to_julian_day(period_to)

    if None in (from_year, to_year):
        return jsonify({'errors': [{
                'status': '400',
                'title': 'Invalid period supplied; must be YYYY-MM-DD,YYYY-MM-DD'
                }]
            }), 400

    #send to sql formatter function
    sql, download_sql = format_terrai_sql(from_year, from_date, to_year, to_date)

    geostore = make_wdpa_request(wdpa_id)[0]
    area = make_wdpa_request(wdpa_id)[1]

    #make request to glad database
    data = make_terrai_request(sql, geostore)

    standard_format = standardize_response(data, "COUNT(day)", '67cf7c03-7365-4a1f-8401-d42c3706b7de', download_sql, area, geostore)

    return jsonify({'data': standard_format}), 200

@endpoints.route('/gladanalysis/date-range', methods=['GET'])
def glad_date_range():

    max_sql = '?sql=select MAX(julian_day)from index_e663eb0904de4f39b87135c6c2ed10b5 where year = 2017'
    min_sql = '?sql=select MIN(julian_day)from index_e663eb0904de4f39b87135c6c2ed10b5 where year = 2015'

    # min_julian = get_date('274b4818-be18-4890-9d10-eae56d2a82e5', min_sql, 'MIN(julian_day)')
    max_julian = get_date('274b4818-be18-4890-9d10-eae56d2a82e5', max_sql, 'MAX(julian_day)')

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

    max_sql = '?sql=select MAX(day)from index_67cf7c0373654a1f8401d42c3706b7de where year = 2017'
    min_sql = '?sql=select MIN(day)from index_67cf7c0373654a1f8401d42c3706b7de where year = 2004'

    # min_julian = get_date('274b4818-be18-4890-9d10-eae56d2a82e5', min_sql, 'MIN(julian_day)')
    max_julian = get_date('67cf7c03-7365-4a1f-8401-d42c3706b7de', max_sql, 'MAX(day)')

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

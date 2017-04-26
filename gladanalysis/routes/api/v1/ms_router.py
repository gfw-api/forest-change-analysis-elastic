import os
import logging
import datetime

from flask import jsonify, request
import requests

from . import endpoints
from gladanalysis.responders import ErrorResponder
from gladanalysis.utils.http import request_to_microservice

# dates should be year then julian dates
# example request: "localhost:9000/gladanalysis?geostore=939a166f7e824f62eb967f7cfb3462ee&period=2016-1-1,2017-1-1&confidence=3"

@endpoints.route('/gladanalysis', methods=['GET'])
def query_glad():
    """Query GLAD"""
    logging.info('QUERYING GLAD')

    geostore = request.args.get('geostore', None)
    period = request.args.get('period', None)
    conf = request.args.get('confidence', None)

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
    if (int(from_year) < 2015 or int(to_year) > 2017):
        return jsonify({'errors': [{
            'status': '400',
            'title': 'GLAD period must be between 2015 and 2017'
            }]
        }), 400
    else:
        sql = "?sql=select count(julian_day) from index_e663eb0904de4f39b87135c6c2ed10b5 where ((year = %s and julian_day >= %s) or (year >= %s and year <= %s) or (year = %s and julian_day <= %s))" %(from_year, from_date, (int(from_year) + 1), to_year, to_year, to_date)
        download_sql = "?sql=select lat, long, confidence, year, julian_day from index_e663eb0904de4f39b87135c6c2ed10b5 where ((year = %s and julian_day >= %s) or (year >= %s and year <= %s) or (year = %s and julian_day <= %s))" %(from_year, from_date, (int(from_year) + 1), to_year, to_year, to_date)

    #create condition to look for confidence filter
    if conf == '3':
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    #format request to glad dataset
    url = 'http://staging-api.globalforestwatch.org/query/'
    datasetID = '274b4818-be18-4890-9d10-eae56d2a82e5'
    f = '&format=json'

    full = url + datasetID + sql + confidence + "&geostore=" + geostore + f
    r = requests.get(url=full)
    data = r.json()

    #format response to geostore to recieve area ha
    area_url = 'http://staging-api.globalforestwatch.org/geostore/' + geostore
    r_area = requests.get(url=area_url)
    area_resp = r_area.json()
    area = area_resp['data']['attributes']['areaHa']

    #standardize response
    standard_format = {}
    standard_format["type"] = "glad-alerts"
    standard_format["id"] = "undefined"
    standard_format["attributes"] = {}
    standard_format["attributes"]["value"] = data["data"][0]["COUNT(julian_day)"]
    standard_format["attributes"]["downloadUrls"] = {}
    standard_format["attributes"]["downloadUrls"]["csv"] = "/download/274b4818-be18-4890-9d10-eae56d2a82e5" + download_sql + "&geostore=" + geostore + "&format=csv"
    standard_format["attributes"]["downloadUrls"]["json"] = "/download/274b4818-be18-4890-9d10-eae56d2a82e5" + download_sql + "&geostore=" + geostore + "&format=json"
    standard_format['attributes']["areaHa"] = area

    return jsonify({'data': standard_format}), 200


def date_to_julian_day(input_date):

    try:
        date_obj = datetime.datetime.strptime(input_date, '%Y-%m-%d')
        time_tuple = date_obj.timetuple()
        logging.info(time_tuple.tm_year)
        return str(time_tuple.tm_year), str(time_tuple.tm_yday)

    except ValueError:
        return None, None

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
    sql = "?sql=select count(day) from index_67cf7c0373654a1f8401d42c3706b7de where ((year = %s and day >= %s) or (year >= %s and year <= %s) or (year = %s and day <= %s))" %(from_year, from_date, (int(from_year) + 1), to_year, to_year, to_date)
    download_sql = "?sql=select lat, long, confidence, year, day from index_67cf7c0373654a1f8401d42c3706b7de where ((year = %s and day >= %s) or (year >= %s and year <= %s) or (year = %s and day <= %s))" %(from_year, from_date, (int(from_year) + 1), to_year, to_year, to_date)

    #format request parameters to Terra I
    url = 'http://staging-api.globalforestwatch.org/query/'
    datasetID = '67cf7c03-7365-4a1f-8401-d42c3706b7de'
    f = '&format=json'

    full = url + datasetID + sql + "&geostore=" + geostore + f
    r = requests.get(url=full)
    data = r.json()

    #format response to geostore to recieve area ha
    area_url = 'http://staging-api.globalforestwatch.org/geostore/' + geostore
    r_area = requests.get(url=area_url)
    area_resp = r_area.json()
    area = area_resp['data']['attributes']['areaHa']

    #standardize response
    standard_format = {}
    standard_format["type"] = "terrai-alerts"
    standard_format["id"] = "undefined"
    standard_format["attributes"] = {}
    standard_format["attributes"]["value"] = data["data"][0]["COUNT(day)"]
    standard_format['attributes']["areaHa"] = area
    standard_format["attributes"]["downloadUrls"] = {}
    standard_format["attributes"]["downloadUrls"]["csv"] = "/download/67cf7c03-7365-4a1f-8401-d42c3706b7de" + download_sql + "&geostore=" + geostore + "&format=csv"
    standard_format["attributes"]["downloadUrls"]["json"] = "/download/67cf7c03-7365-4a1f-8401-d42c3706b7de" + download_sql + "&geostore=" + geostore + "&format=json"

    return jsonify({'data': standard_format}), 200

@endpoints.route('/gladanalysis/admin/<iso_code>/<admin_id>', methods=['GET'])
def glad_country(iso_code, admin_id):

    logging.info('Running GADM level glad analysis')

    #accept period parameter
    period = request.args.get('period', None)
    conf = request.args.get('gladConfirmOnly', None)

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

    #format SQL statements
    if (int(from_year) < 2015 or int(to_year) > 2017):
        return jsonify({'errors': [{
            'status': '400',
            'title': 'GLAD period must be between 2015 and 2017'
            }]
        }), 400
    else:
        sql = "?sql=select count(julian_day) from index_e663eb0904de4f39b87135c6c2ed10b5 where ((year = %s and julian_day >= %s) or (year >= %s and year <= %s) or (year = %s and julian_day <= %s))" %(from_year, from_date, (int(from_year) + 1), to_year, to_year, to_date)
        download_sql = "?sql=select lat, long, confidence, year, julian_day from index_e663eb0904de4f39b87135c6c2ed10b5 where ((year = %s and julian_day >= %s) or (year >= %s and year <= %s) or (year = %s and julian_day <= %s))" %(from_year, from_date, (int(from_year) + 1), to_year, to_year, to_date)

    #get geostore id from admin areas and total area of geostore request
    geostore_url = 'https://staging-api.globalforestwatch.org/geostore/admin/%s/%s'%(iso_code, admin_id)
    r = requests.get(url=geostore_url)
    geostore_data = r.json()
    geostore = geostore_data['data']['id']
    area_ha = geostore_data['data']['attributes']['areaHa']

    #format request to elastic database of glad alerts

    glad_url = 'http://staging-api.globalforestwatch.org/query/'
    datasetID = '274b4818-be18-4890-9d10-eae56d2a82e5'
    f = '&format=json'

    if conf == 'true':
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    full = glad_url + datasetID + sql + confidence + "&geostore=" + geostore + f
    r = requests.get(url=full)
    glad_data = r.json()

    #standardize response
    standard_format = {}
    standard_format["type"] = "glad-alerts"
    standard_format["id"] = "undefined"
    standard_format["attributes"] = {}
    standard_format["attributes"]["value"] = glad_data["data"][0]["COUNT(julian_day)"]
    standard_format["attributes"]["downloadUrls"] = {}
    standard_format["attributes"]["downloadUrls"]["csv"] = "/download/274b4818-be18-4890-9d10-eae56d2a82e5" + download_sql + "&geostore=" + geostore + "&format=csv"
    standard_format["attributes"]["downloadUrls"]["json"] = "/download/274b4818-be18-4890-9d10-eae56d2a82e5" + download_sql + "&geostore=" + geostore + "&format=json"
    standard_format['attributes']["areaHa"] = area_ha

    return jsonify({'data': standard_format}), 200

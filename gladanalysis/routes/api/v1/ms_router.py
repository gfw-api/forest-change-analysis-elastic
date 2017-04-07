import os
import logging
import datetime

from flask import jsonify, request
import requests

from . import endpoints
from gladanalysis.responders import ErrorResponder
from gladanalysis.utils.http import request_to_microservice

#dates should be year then julian dates
#example request: "localhost:9000/gladanalysis?geostore=939a166f7e824f62eb967f7cfb3462ee&period=2016-1-1,2017-1-1&confidence=3"

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

    if (from_year == '2015') and (to_year == '2017'):
        sql = "?sql=select count(julian_day) from index_e663eb0904de4f39b87135c6c2ed10b5 where ((year = '2015' and julian_day >= %s) or (year = '2016') or (year = '2017' and julian_day <= %s))" %(from_date, to_date)
        download_sql = "?sql=select lat, long, confidence, year, julian_day from index_e663eb0904de4f39b87135c6c2ed10b5 where ((year = '2015' and julian_day >= %s) or (year = '2016') or (year = '2017' and julian_day <= %s))" %(from_date, to_date)
    elif (from_year == '2015') and (to_year == '2016'):
        sql = "?sql=select count(julian_day) from index_e663eb0904de4f39b87135c6c2ed10b5 where ((year = '2015' and julian_day >= %s) or (year = '2016' and julian_day <= %s))" %(from_date, to_date)
        download_sql = "?sql=select lat, long, confidence, year, julian_day from index_e663eb0904de4f39b87135c6c2ed10b5 where ((year = '2015' and julian_day >= %s) or (year = '2016' and julian_day <= %s))" %(from_date, to_date)
    elif (from_year == '2016') and (to_year == '2017'):
        sql = "?sql=select count(julian_day) from index_e663eb0904de4f39b87135c6c2ed10b5 where ((year = '2016' and julian_day >= %s) or (year = '2017' and julian_day <= %s))" %(from_date, to_date)
        download_sql = "?sql=select lat, long, confidence, year, julian_day from index_e663eb0904de4f39b87135c6c2ed10b5 where ((year = '2016' and julian_day >= %s) or (year = '2017' and julian_day <= %s))" %(from_date, to_date)
    elif (from_year == '2015') and (to_year == '2015'):
        sql = "?sql=select count(julian_day) from index_e663eb0904de4f39b87135c6c2ed10b5 where year = '2015' and julian_day >= %s and julian_day <= %s" %(from_date, to_date)
        download_sql = "?sql=select lat, long, confidence, year, julian_day from index_e663eb0904de4f39b87135c6c2ed10b5 where year = '2015' and julian_day >= %s and julian_day <= %s" %(from_date, to_date)
    elif (from_year == '2016') and (to_year == '2016'):
        sql = "?sql=select count(julian_day) from index_e663eb0904de4f39b87135c6c2ed10b5 where year = '2016' and julian_day >= %s and julian_day <= %s" %(from_date, to_date)
        download_sql = "?sql=select lat, long, confidence, year, julian_day from index_e663eb0904de4f39b87135c6c2ed10b5 where year = '2016' and julian_day >= %s and julian_day <= %s" %(from_date, to_date)
    elif (from_year == '2017') and (to_year == '2017'):
        sql = "?sql=select count(julian_day) from index_e663eb0904de4f39b87135c6c2ed10b5 where year = '2017' and julian_day >= %s and julian_day <= %s" %(from_date, to_date)
        download_sql = "?sql=select lat, long, confidence, year, julian_day from index_e663eb0904de4f39b87135c6c2ed10b5 where year = '2017' and julian_day >= %s and julian_day <= %s" %(from_date, to_date)
    else:
        return jsonify({'errors': [{
            'status': '400',
            'title': 'GLAD period must be between 2015 and 2017'
            }]
        }), 400

    if conf == '3':
        confidence = "and confidence = '3'"
    else:
        confidence = ""

    url = 'http://staging-api.globalforestwatch.org/query/'
    datasetID = '274b4818-be18-4890-9d10-eae56d2a82e5'
    f = '&format=json'

    full = url + datasetID + sql + confidence + "&geostore=" + geostore + f
    r = requests.get(url=full)
    data = r.json()

    area_url = 'http://staging-api.globalforestwatch.org/geostore/' + geostore
    r_area = requests.get(url=area_url)
    area_resp = r_area.json()
    area = area_resp['data']['attributes']['areaHa']

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


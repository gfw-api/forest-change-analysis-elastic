import json
import datetime
import logging
import requests


class DateService(object):

    @staticmethod
    def date_to_julian_day(period):
        #Helper function to transform dates
        try:
    	    period_from = period.split(',')[0]
    	    period_to = period.split(',')[1]
    	    date_obj_from = datetime.datetime.strptime(period_from, '%Y-%m-%d')
    	    date_obj_to = datetime.datetime.strptime(period_to, '%Y-%m-%d')
    	    time_tuple_from = date_obj_from.timetuple()
    	    time_tuple_to = date_obj_to.timetuple()
    	    logging.info(time_tuple_from.tm_year)
    	    logging.info(time_tuple_to.tm_year)
    	    return str(time_tuple_from.tm_year), str(time_tuple_from.tm_yday), str(time_tuple_to.tm_year), str(time_tuple_to.tm_yday)

        except ValueError:
            return None, None

    @staticmethod
    def get_date(datasetID, sql, value):

        url = 'http://staging-api.globalforestwatch.org/query/'
        f = '&format=json'

        full = url + datasetID + sql + f
        r = requests.get(url=full)
        values = r.json()
        date_value = values['data'][0][value]
        return date_value

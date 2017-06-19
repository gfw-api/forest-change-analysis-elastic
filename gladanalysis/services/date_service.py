import json
import datetime
import logging
import calendar

from CTRegisterMicroserviceFlask import request_to_microservice
from sql_service import SqlService

class DateService(object):
    """Class for formatting dates"""

    @staticmethod
    def date_to_julian_day(period=None, datasetID=None, indexID=None):
        #Helper function to transform dates
        if period == None:
            from_year, from_date, to_year, to_date = SqlService.get_min_max_date(datasetID, indexID)
            return from_year, from_date, to_year, to_date
        else:
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
    def julian_day_to_date(year, jd):
        month = 1
        day = 0
        while jd - calendar.monthrange(year,month)[1] > 0 and month < 12:
            jd = jd - calendar.monthrange(year,month)[1]
            month = month + 1
        return year, month, jd

    @staticmethod
    def get_date(datasetID, sql, value):

        uri = "/query/%s" %(datasetID) + sql + '&format=json'

        config = {
        'uri': uri,
        'method': 'GET'
        }

        values = request_to_microservice(config)
        date_value = values['data'][0][value]
        return date_value

import json
import datetime
import logging
import calendar

from CTRegisterMicroserviceFlask import request_to_microservice

class DateService(object):
    """Class for formatting dates"""

    @staticmethod
    def date_to_julian_day(self, period=None, datasetID=None, indexID=None):
        #Helper function to transform dates
        if period == None:
            from_year, from_date, to_year, to_date = DateService.get_min_max_date(datasetID, indexID)
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

    @staticmethod
    def get_min_max_date(self, datasetID, indexID):

        #Get max year from database
        max_year_sql = '?sql=select MAX(year)from {}'.format(indexID)
        max_year = DateService.get_date(datasetID, max_year_sql, 'MAX(year)')

        #Get max julian date from database
        max_sql = '?sql=select MAX(julian_day)from {} where year = {}'.format(indexID, max_year)
        max_julian = DateService.get_date(datasetID, max_sql, 'MAX(julian_day)')

        #Get min year from database
        min_year_sql = '?sql=select MIN(year)from {}'.format(indexID)
        min_year = DateService.get_date(datasetID, min_year_sql, 'MIN(year)')

        #Get min date from database
        min_day_sql = '?sql=select MIN(julian_day)from {} where year = {}'.format(indexID, min_year)
        min_julian = DateService.get_date(datasetID, min_day_sql, 'MIN(julian_day)')

        return min_year, min_julian, max_year, max_julian

    @staticmethod
    def format_date_sql(self, min_year, min_julian, max_year, max_julian):

        #convert julian to date format
        max_y, max_m, max_d = DateService.julian_day_to_date(max_year, max_julian)
        min_y, min_m, min_d = DateService.julian_day_to_date(min_year, min_julian)

        #format dates
        max_date = '%s-%02d-%s' %(max_y, max_m, max_d)
        min_date = '%s-%02d-%s' %(min_y, min_m, min_d)

        return min_date, max_date

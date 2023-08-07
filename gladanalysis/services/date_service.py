import calendar
import datetime
import json
import logging

from RWAPIMicroservicePython import request_to_microservice


class DateService(object):
    """Class for formatting dates
    Contains a number of methods for converting the period param to useful formats"""

    @staticmethod
    def date_to_julian_day(api_key, period=None, dataset_id=None, index_id=None, value=None):
        # Helper function to transform dates
        if period is None:
            from_year, from_date, to_year, to_date = DateService.get_min_max_date(value, dataset_id, index_id, api_key)
            return from_year, from_date, to_year, to_date
        else:
            try:
                period_from, period_to = period.split(',')
                date_obj_from = datetime.datetime.strptime(period_from, '%Y-%m-%d')
                date_obj_to = datetime.datetime.strptime(period_to, '%Y-%m-%d')

                time_tuple_from = date_obj_from.timetuple()
                time_tuple_to = date_obj_to.timetuple()

                return str(time_tuple_from.tm_year), str(time_tuple_from.tm_yday), str(time_tuple_to.tm_year), str(
                    time_tuple_to.tm_yday)

            except ValueError:
                return None, None

    @staticmethod
    def julian_day_to_date(year, jd):
        month = 1
        while jd - calendar.monthrange(year, month)[1] > 0 and month < 12:
            jd = jd - calendar.monthrange(year, month)[1]
            month = month + 1
        return year, month, jd

    @staticmethod
    def get_date(dataset_id, sql, value, api_key):

        uri = "/v1/query/%s" % dataset_id + sql + '&format=json'

        config = {
            'uri': uri,
            'method': 'GET',
            'api_key': api_key
        }
        logging.info('Making request to other MS: ' + json.dumps(config))

        values = request_to_microservice(**config)
        date_value = values['data'][0][value]
        return date_value

    @staticmethod
    def get_min_max_date(value, dataset_id, index_id, api_key):

        # set variables for alert values
        max_value = 'MAX({})'.format(value)
        min_value = 'MIN({})'.format(value)

        # Get max year from database
        max_year_sql = '?sql=select MAX(year)from {}'.format(index_id)
        max_year = DateService.get_date(dataset_id, max_year_sql, 'MAX(year)', api_key)

        # Get max julian date from database
        max_sql = '?sql=select {}from {} where year = {}'.format(max_value, index_id, max_year)
        max_julian = DateService.get_date(dataset_id, max_sql, max_value, api_key)

        # Get min year from database
        min_year_sql = '?sql=select MIN(year)from {} WHERE year > 2000'.format(index_id)
        min_year = DateService.get_date(dataset_id, min_year_sql, 'MIN(year)', api_key)

        # Get min date from database
        min_day_sql = '?sql=select {}from {} where year = {}'.format(min_value, index_id, min_year)
        min_julian = DateService.get_date(dataset_id, min_day_sql, min_value, api_key)

        return min_year, min_julian, max_year, max_julian

    @staticmethod
    def format_date_sql(min_year, min_julian, max_year, max_julian):

        # convert julian to date format
        max_y, max_m, max_d = DateService.julian_day_to_date(max_year, max_julian)
        min_y, min_m, min_d = DateService.julian_day_to_date(min_year, min_julian)

        # format dates
        max_date = '%s-%02d-%02d' % (max_y, max_m, max_d)
        min_date = '%s-%02d-%02d' % (min_y, min_m, min_d)

        return min_date, max_date

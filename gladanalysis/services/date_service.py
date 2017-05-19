import json
import requests


class DateService(object):

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

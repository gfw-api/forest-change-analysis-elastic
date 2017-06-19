from flask import jsonify
import os

class SqlService(object):
    """Class for formatting query and donwload sql"""

    @staticmethod
    def format_glad_sql(conf, from_year, from_date, to_year, to_date, iso=None, state=None, dist=None):

        select_sql = 'SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day '
        count_sql = 'SELECT count(julian_day) '
        from_sql = 'FROM {} '.format(os.getenv('GLAD_INDEX_ID'))
        order_sql = 'ORDER BY year, julian_day'

        if conf == 'true' or conf == 'True':
            confidence = "and confidence = '3'"
        else:
            confidence = ""

        if (from_year == '2015') and (to_year == '2017'):
            where_template = ("WHERE ((year = '2015' and julian_day >= {d1}) or "
            "(year = '2016') or "
            "(year = '2017' and julian_day <= {d2}))") + confidence

        elif from_year == to_year:
            where_template = 'WHERE ((year = {y1} and julian_day >= {d1} and julian_day <= {d2}))' + confidence

        else:
            where_template = 'WHERE ((year = {y1} and julian_day >= {d1}) or (year = {y2} and julian_day <= {d2}))' + confidence

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

    @staticmethod
    def format_terrai_sql(from_year, from_date, to_year, to_date, iso=None, state=None, dist=None):

        select_sql = 'SELECT lat, long, country_iso, state_id, dist_id, year, day '
        count_sql = 'SELECT count(day) '
        from_sql = 'FROM {} '.format(os.getenv('TERRAI_INDEX_ID'))
        order_sql = 'ORDER BY year, day'

        if (int(from_year) == int(to_year)):
            where_template = 'WHERE ((year = {y1} and day >= {d1} and day <= {d2}))'

        elif (int(from_year) + 1) == int(to_year):
            where_template = 'WHERE ((year = {y1} and day >= {d1}) or (year = {y2} and day <= {d2}))'

        else:
            where_template = 'WHERE ((year = {y1} and day >= {d1}) or (year >= {y1_plus_1} and year <= {y2_minus_1}) or (year = {y2} and day <= {d2}))'

        geog_id_list = ['country_iso', 'state_id', 'dist_id']
        geog_val_list = [iso, state, dist]

        for geog_name, geog_value in zip(geog_id_list, geog_val_list):
            if geog_value:
                if geog_name == 'country_iso':
                    where_template += " AND ({} = '{}')".format(geog_name, geog_value)
                else:
                    where_template += ' AND ({} = {})'.format(geog_name, geog_value)

        where_sql = where_template.format(y1=int(from_year), d1=int(from_date), y1_plus_1=(int(from_year) + 1), y2=int(to_year), d2=int(to_date), y2_minus_1=(int(to_year) - 1))

        sql = '?sql=' + ''.join([count_sql, from_sql, where_sql])
        download_sql = '?sql=' + ''.join([select_sql, from_sql, where_sql, order_sql])

        return sql, download_sql

    @staticmethod
    def get_min_max_date(datasetID, indexID):

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
    def format_date_sql(min_year, min_julian, max_year, max_julian):

        #convert julian to date format
        max_y, max_m, max_d = DateService.julian_day_to_date(max_year, max_julian)
        min_y, min_m, min_d = DateService.julian_day_to_date(min_year, min_julian)

        #format dates
        max_date = '%s-%02d-%s' %(max_y, max_m, max_d)
        min_date = '%s-%02d-%s' %(min_y, min_m, min_d)

        return min_date, max_date

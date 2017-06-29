from flask import jsonify, request
import os

class SqlService(object):
    """Class for formatting query and donwload sql"""

    @staticmethod
    def format_glad_sql(conf, from_year, from_date, to_year, to_date, iso=None, state=None, dist=None):

        """set sql variables for glad"""
        select_sql = 'SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day '
        count_sql = 'SELECT count(julian_day) '
        from_sql = 'FROM {} '.format(os.getenv('GLAD_INDEX_ID'))
        order_sql = 'ORDER BY year, julian_day'

        """set confidence variable for glad"""
        if conf == 'true' or conf == 'True':
            confidence = "and confidence = '3'"
        else:
            confidence = ""

        """set date variables for glad"""
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

        sql = ''.join([count_sql, from_sql, where_sql])
        download_sql = ''.join([select_sql, from_sql, where_sql, order_sql])

        if request.method == 'GET':
            sql = '?sql=' + sql
            download_sql = '?sql=' + download_sql
            return sql, download_sql
        elif request.method == 'POST':
            return sql

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

        sql = ''.join([count_sql, from_sql, where_sql])
        download_sql = ''.join([select_sql, from_sql, where_sql, order_sql])

        if request.method == 'GET':
            sql = '?sql=' + sql
            download_sql = '?sql=' + download_sql
            return sql, download_sql
        elif request.method == 'POST':
            return sql

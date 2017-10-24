from flask import jsonify, request
import os

class QueryConstructorService(object):
    """Class for formatting query and donwload sql"""

    @staticmethod
    def format_dataset_query(day_value, confidence, from_year, from_date, to_year, to_date, count_sql, from_sql, select_sql, order_sql, groupby_sql, iso=None, state=None, dist=None):

        if (int(from_year) == int(to_year)):
            where_template = 'WHERE ((year = {y1} and {day} >= {d1} and {day} <= {d2}))' + confidence

        elif (int(from_year) + 1) == int(to_year):
            where_template = 'WHERE ((year = {y1} and {day} >= {d1}) or (year = {y2} and {day} <= {d2}))' + confidence

        else:
            where_template = 'WHERE ((year = {y1} and {day} >= {d1}) or (year >= {y1_plus_1} and year <= {y2_minus_1}) or (year = {y2} and {day} <= {d2}))' + confidence

        geog_id_list = ['country_iso', 'state_id', 'dist_id']
        geog_val_list = [iso, state, dist]

        for geog_name, geog_value in zip(geog_id_list, geog_val_list):
            if geog_value:
                if geog_name == 'country_iso':
                    where_template += " AND ({} = '{}')".format(geog_name, geog_value)
                else:
                    where_template += ' AND ({} = {})'.format(geog_name, geog_value)

        where_sql = where_template.format(y1=int(from_year), d1=int(from_date), y1_plus_1=(int(from_year) + 1), y2=int(to_year), d2=int(to_date), y2_minus_1=(int(to_year) - 1), day=day_value)

        sql = ''.join(filter(None, [count_sql, from_sql, where_sql, groupby_sql]))
        download_sql = '?sql=' + ''.join([select_sql, from_sql, where_sql, order_sql])

        return sql, download_sql

    @staticmethod
    def format_glad_sql(conf, from_year, from_date, to_year, to_date, iso=None, state=None, dist=None, agg_values=False):

        """set sql variables for glad"""
        select_sql = 'SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day '

        if agg_values:
            count_sql = 'SELECT year, julian_day, count(*)'
        else:
            count_sql = 'SELECT count(julian_day) '

        from_sql = 'FROM {} '.format(os.getenv('GLAD_INDEX_ID'))
        order_sql = 'ORDER BY year, julian_day'

        if agg_values:
            groupby_sql = 'GROUP BY year, julian_day'
        else:
            groupby_sql = None

        """set confidence variable for glad"""
        if conf == 'false' or conf == 'False':
            confidence = ""
        elif conf or conf == 'true' or conf == 'True':
            confidence = "and confidence = '3'"
        else:
            confidence = ""

        sql, download_sql = QueryConstructorService.format_dataset_query("julian_day", confidence, from_year, from_date, to_year, to_date, count_sql, from_sql, select_sql, order_sql, groupby_sql, iso=iso, state=state, dist=dist)

        return sql, download_sql

    @staticmethod
    def format_terrai_sql(from_year, from_date, to_year, to_date, iso=None, state=None, dist=None, agg_values=False):

        select_sql = 'SELECT lat, long, country_iso, state_id, dist_id, year, day '

        if agg_values:
            count_sql = 'SELECT year, day, count(*)'
        else:
            count_sql = 'SELECT count(day) '

        from_sql = 'FROM {} '.format(os.getenv('TERRAI_INDEX_ID'))
        order_sql = 'ORDER BY year, day'

        if agg_values:
            groupby_sql = 'GROUP BY year, day'
        else:
            groupby_sql = None

        sql, download_sql = QueryConstructorService.format_dataset_query("day", "", from_year, from_date, to_year, to_date, count_sql, from_sql, select_sql, order_sql, groupby_sql, iso=iso, state=state, dist=dist)

        return sql, download_sql

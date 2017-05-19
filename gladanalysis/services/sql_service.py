from flask import jsonify, request
import requests
import os


class SqlService(object):

    @staticmethod
    def format_glad_sql(from_year, from_date, to_year, to_date, iso=None, state=None, dist=None):

        select_sql = 'SELECT lat, long, confidence_text, country_iso, state_id, dist_id, year, julian_day '
        count_sql = 'SELECT count(julian_day) '
        from_sql = 'FROM {} '.format(os.getenv('GLAD_INDEX_ID'))
        order_sql = 'ORDER BY year, julian_day'

        if (int(from_year) < 2015 or int(to_year) > 2017):
            return jsonify({'errors': [{
                'status': '400',
                'title': 'GLAD period must be between 2015 and 2017'
                }]
            }), 400

        elif (from_year == '2015') and (to_year == '2017'):
            where_template = ("WHERE ((year = '2015' and julian_day >= {d1}) or "
            "(year = '2016') or "
            "(year = '2017' and julian_day <= {d2}))")

        elif from_year == to_year:
            where_template = 'WHERE ((year = {Y1} and julian_day >= {d1} and julian_day <= {d2}))'

        else:
            where_template = 'WHERE ((year = {y1} and julian_day >= {d1}) or (year = {y2} and julian_day <= {d2}))'

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

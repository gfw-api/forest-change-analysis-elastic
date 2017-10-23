"""VALIDATORS"""

import datetime
import re

from functools import wraps
from flask import request

from gladanalysis.routes.api.v2 import error

def validate_geostore(func):
    """validate geostore argument"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        if request.method == 'GET':
            geostore = request.args.get('geostore')
        elif request.method == 'POST':
            geostore = request.get_json().get('geojson', None) if request.get_json() else None

        if not geostore:
            return error(status=400, detail="Geostore or geojson must be set")

        return func(*args, **kwargs)
    return wrapper

def validate_agg(func):
    """validate aggregate_by argument"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        if request.method == 'GET':
            agg_by = request.args.get('aggregate_by')
            agg_values = request.args.get('aggregate_values')
        elif request.method == 'POST':
            agg_by = request.get_json().get('aggregate_by', None) if request.get_json() else None
            agg_values = request.get_json().get('aggregate_values', None) if request.get_json() else None

        if agg_values:
            if agg_values.lower() not in ['true', 'false']:
                return error(status=400, detail="aggregate_values parameter not "
                             "must be either true or false")

            agg_values = eval(agg_values.title())

        if agg_values and agg_by:
            agg_list = ['day', 'week', 'quarter', 'month', 'year', 'julian_day']

            if agg_by.lower() not in agg_list:
                return error(status=400, detail="aggregate_by parameter not "
                             "in: {}".format(agg_list))

        if agg_by and not agg_values:
            return error(status=400, detail="aggregate_values parameter must be "
                                            "true in order to aggregate data")

        return func(*args, **kwargs)
    return wrapper

def validate_glad_period(func):
    """validate period argument"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        error = validate_period(2015)
        if error:
            return error

        return func(*args, **kwargs)
    return wrapper

def validate_terrai_period(func):
    """validate period argument"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        error = validate_period(2004)
        if error:
            return error

        return func(*args, **kwargs)
    return wrapper

def validate_period(minYear):

    today = datetime.datetime.now()
    period = request.args.get('period', None)

    if period:
        if len(period.split(',')) < 2:
            return error(status=400, detail="Period needs 2 arguments")

        else:
            period_from = period.split(',')[0]
            period_to = period.split(',')[1]

            try:
                period_from = datetime.datetime.strptime(period_from, '%Y-%m-%d')
                period_to = datetime.datetime.strptime(period_to, '%Y-%m-%d')
            except ValueError:
                return error(status=400, detail="Incorrect format, should be YYYY-MM-DD,YYYY-MM-DD")

            if period_from.year < minYear:
                return error(status=400, detail="Start date can't be earlier than {}-01-01".format(minYear))
                
            if period_to.year > today.year:
                return error(status=400, detail="End year can't be later than {}".format(today.year))

            if period_from > period_to:
                return error(status=400, detail='Start date must be less than end date')


def validate_use(func):
    """Use Validation"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        names = ['mining', 'oilpalm', 'fiber', 'logging']
        name = request.view_args.get('use_type')
        use_id = request.view_args.get('use_id')

        if not name or not use_id:
            return error(status=400, detail="Use Type (mining, oilpalm, fiber, or logging), and Use ID must be set")

        elif name not in names:
            return error(status=400, detail='Use Type not valid (valid options: mining, oilpalm, fiber, or logging)')

        elif re.search('[a-zA-Z]', use_id):
            return error(status=400, detail="Use ID should be numeric")

        return func(*args, **kwargs)
    return wrapper

def validate_admin(func):
    """validate admin arguments"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        iso_code = request.view_args.get('iso_code')
        admin_id = request.view_args.get('admin_id')
        dist_id = request.view_args.get('dist_id')

        if not iso_code:
            return error(status=400, detail="Must specify a ISO code, and optionally a /state_id and /ditrict_id")

        elif len(iso_code) > 3 or len(iso_code) < 3:
            return error(status=400, detail="Must use a 3-letter ISO Code")

        elif admin_id:
            if re.search('[a-zA-Z]', admin_id):
                return error(status=400, detail="For state and district queries please use numbers")

            else:
                pass

        elif dist_id:
            if re.search('[a-zA-Z]', dist_id):
                return error(status=400, detail="For state and district queries please use numbers")

            else:
                pass

        return func(*args, **kwargs)
    return wrapper

def validate_wdpa(func):
    """validate geostore argument"""
    @wraps(func)
    def wrapper(*args, **kwargs):

        wdpa_id = request.view_args.get('wdpa_id')

        if not wdpa_id:
            return error(status=400, detail="WDPA ID should be set")

        elif re.search('[a-zA-Z]', wdpa_id):
            return error(status=400, detail="WDPA ID should be numeric")

        return func(*args, **kwargs)
    return wrapper

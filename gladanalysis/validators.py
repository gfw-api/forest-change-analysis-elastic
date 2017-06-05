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

            if not geostore:
                return error(status=400, detail="Geostore must be set")

        return func(*args, **kwargs)
    return wrapper

def validate_glad_period(func):
    """validate period argument"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'GET':
            period = request.args.get('period')

            if not period:
                return error(status=400, detail="Time period must be set")

            elif len(period.split(',')) < 2:
                return error(status=400, detail="Period needs 2 arguments")

            else:
                period_from = period.split(',')[0]
                period_to = period.split(',')[1]

                try:
                    datetime.datetime.strptime(period_from, '%Y-%m-%d')
                except ValueError:
                    return error(status=400, detail="incorrect format, should be YYYY-MM-DD")

                try:
                    datetime.datetime.strptime(period_to, '%Y-%m-%d')
                except ValueError:
                    return error(status=400, detail="incorrect format, should be YYYY-MM-DD")

                if int(period_from.split('-')[0]) < 2015:
                    return error(status=400, detail="start date can't be earlier than 2015-01-01")
                elif int(period_to.split('-')[0]) > 2017:
                    return error(status=400, detail="end year can't be later than 2017")

        return func(*args, **kwargs)
    return wrapper

def validate_terrai_period(func):
    """validate period argument"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'GET':
            period = request.args.get('period')

            if not period:
                return error(status=400, detail="Time period must be set")

            elif len(period.split(',')) < 2:
                return error(status=400, detail="Period needs 2 arguments")

            else:
                period_from = period.split(',')[0]
                period_to = period.split(',')[1]

                try:
                    datetime.datetime.strptime(period_from, '%Y-%m-%d')
                except ValueError:
                    return error(status=400, detail="incorrect format, should be YYYY-MM-DD")

                try:
                    datetime.datetime.strptime(period_to, '%Y-%m-%d')
                except ValueError:
                    return error(status=400, detail="incorrect format, should be YYYY-MM-DD")

                if int(period_from.split('-')[0]) < 2004:
                    return error(status=400, detail="start date can't be earlier than 2004-01-01")
                elif int(period_to.split('-')[0]) > 2017:
                    return error(status=400, detail="end year can't be later than 2017")

        return func(*args, **kwargs)
    return wrapper

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
        if request.method == 'GET':
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

        if request.method == 'GET':
            wdpa_id = request.view_args.get('wdpa_id')

            if not wdpa_id:
                return error(status=400, detail="WDPA ID should be set")

            elif re.search('[a-zA-Z]', wdpa_id):
                return error(status=400, detail="WDPA ID should be numeric")

        return func(*args, **kwargs)
    return wrapper

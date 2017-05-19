"""VALIDATORS"""

from functools import wraps
from flask import request

from gladanalysis.routes.api.v1 import error

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

def validate_period(func):
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
            return error(status=400, detail="Use Type must be set (mining, oilpalm, fiber, or logging), and Use ID")
        elif name not in names:
            return error(status=400, detail='Use Type not valid (valid options: mining, oilpalm, fiber, or logging)')
        return func(*args, **kwargs)
    return wrapper

def validate_admin(func):
    """validate admin arguments"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'GET':
            iso_code = request.view_args.get('iso_code')
            if not iso_code:
                return error(status=400, detail="Must specify a ISO code, and optionally a /state_id and /ditrict_id")
        return func(*args, **kwargs)
    return wrapper

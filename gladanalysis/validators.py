"""VALIDATORS"""

from functools import wraps
from flask import request

from gladanalysis.routes.api.v1 import error

def validate_geostore_period(func):
    """validate geostore argument"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'GET':
            geostore = request.args.get('geostore')
            period = request.args.get('period')
            if not geostore or not period:
                return error(status=400, detail="Geostore and time period must be set")
        return func(*args, **kwargs)
    return wrapper

def validate_period(func):
    """validate period argument"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'GET':
            period = request.args.get('period')
            if len(period.split(',')) < 2:
                return error(status=400, detail="Period needs 2 arguments")
        return func(*args, **kwargs)
    return wrapper

"""VALIDATORS"""

from functools import wraps
from flask import request

from gladanalysis.routes.api.v1 import error

def validate_geostore_period(func):
    """validate request arguments"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'GET':
            geostore = request.args.get('geostore')
            if not geostore:
                return error(status=400, detail="Geostore must be set")
            period = request.args.get('period')
            if not period:
                return error(status=400, detail="Time period must be set")
        return func(*args, **kwargs)
    return wrapper

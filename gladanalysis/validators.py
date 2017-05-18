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

# def validate_period(func):
#     """validate period argument"""
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         if request.method == 'GET':
#             period = request.args.get('period')
#             if not period:
#                 return error(status=400, detail="Time period must be set")
#         return func(*args, **kwargs)
#     return wrapper

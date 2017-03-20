from hyp.marshmallow import Responder
from gladanalysis.schemas import ErrorSchema


class ErrorResponder(Responder):
    TYPE = 'errors'
    SERIALIZER = ErrorSchema

from marshmallow import Schema, fields


class ErrorSchema(Schema):
    status = fields.Integer()
    message = fields.Str()

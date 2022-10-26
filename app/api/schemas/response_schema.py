from marshmallow import Schema, fields


class ResponseSchema(Schema):
    message = fields.Str(default="Success")


class GoogleAuthResponseSchema(Schema):
    message = fields.Str(default="Success")
    url = fields.Str(default="")

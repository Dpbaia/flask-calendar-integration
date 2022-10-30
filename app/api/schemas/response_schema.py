from marshmallow import Schema, fields


class ResponseSchema(Schema):
    message = fields.Str(default="Success")


class GoogleAuthResponseSchema(Schema):
    message = fields.Str(default="Success")
    url = fields.Str(default="")


class GoogleCalendarResponseSchema(Schema):
    message = fields.Str(default="Success")
    busyTimes = fields.List(fields.Str(), default=[])
    weekday = fields.Str(default="")

from marshmallow import Schema, fields


class ResponseSchema(Schema):
    message = fields.Str(default="Success")


class GoogleAuthResponseSchema(Schema):
    message = fields.Str(default="Success")
    url = fields.Str(default="")


class GoogleDateSchema(Schema):
    end = fields.Str()
    start = fields.Str()


class GoogleCalendarResponseSchema(Schema):
    message = fields.Str(default="Success")
    busyTimes = fields.List(fields.Nested(GoogleDateSchema()), default=[])
    weekday = fields.Str()

from marshmallow import Schema, fields


class RequestSchema(Schema):
    api_type = fields.String(required=True, description="API type of awesome API")


class RequestDateSchema(Schema):
    date = fields.String(required=False, description="dd-mm-yyyy")

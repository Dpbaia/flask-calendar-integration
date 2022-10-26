from marshmallow import Schema, fields


class RequestSchema(Schema):
    api_type = fields.String(required=True, description="API type of awesome API")

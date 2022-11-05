from marshmallow import Schema, fields, validate


class RequestSchema(Schema):
    api_type = fields.String(required=True, description="API type of awesome API")


class RequestDateSchema(Schema):
    date = fields.String(required=False, description="dd-mm-yyyy")


class RequestConsultationSchema(Schema):
    date = fields.String(required=True, description="Day of consultation: dd-mm-yyyy")
    time = fields.String(required=True, description="Hour of the consultation: hh:mm")
    length = fields.String(
        required=True,
        description="How many minutes the consultation will be (hh:mm)",
    )
    email = fields.Email(required=True, description="User email")

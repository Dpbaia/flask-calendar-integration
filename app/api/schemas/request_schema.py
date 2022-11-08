from marshmallow import Schema, fields


class RequestDateSchema(Schema):
    date = fields.String(required=False, description="dd-mm-yyyy")


class RequestAdminId(Schema):
    admin = fields.String(required=False, description="Admin key")


class RequestConsultationSchema(Schema):
    date = fields.String(required=True, description="Day of consultation: dd-mm-yyyy")
    time = fields.String(required=True, description="Hour of the consultation: hh:mm")
    length = fields.String(
        required=True,
        description="How many minutes the consultation will be (hh:mm)",
    )
    email = fields.Email(required=True, description="User email")

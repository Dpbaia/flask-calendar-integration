from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_login import login_required
from flask_restful import Resource
from googleapiclient.errors import HttpError
from icecream import ic

from ...controllers.google_calendar import GoogleCalendarsController
from ...schemas.request_schema import RequestConsultationSchema, RequestDateSchema
from ...schemas.response_schema import (
    GoogleCalendarComparisonResponseSchema,
    GoogleCalendarResponseSchema,
)

# TODO see folder ref

calendar_controller = GoogleCalendarsController()


class GoogleCalendar(MethodResource, Resource):
    @doc(
        description="List events for one month starting from the current date",
        tags=["Google", "Google Calendar"],
    )
    @use_kwargs(RequestDateSchema, location=("query"))
    @marshal_with(GoogleCalendarComparisonResponseSchema)
    @login_required
    def get(self, date=None):
        if date:
            info_owner = calendar_controller.get_single_day_calendar(date)
            info_user = calendar_controller.get_single_day_calendar(date, True)
        else:
            info_owner = calendar_controller.get_thirty_days_calendar()
            info_user = calendar_controller.get_thirty_days_calendar(True)
        info = {"owner": info_owner, "user": info_user}
        ic(info)
        return info, 200

    @doc(description="Create a consultation time", tags=["Google", "Google Calendar"])
    @use_kwargs(RequestConsultationSchema, location=("query"))
    @marshal_with(GoogleCalendarResponseSchema)
    @login_required
    def post(self, date, time, length, email):
        try:
            creds = calendar_controller.get_google_authorization()
        except HttpError as error:
            return {"message": "Error authenticating: " + str(error)}
        try:
            weekday = calendar_controller.create_event(creds, date, time, length, email)
        except HttpError as error:
            return {"message": "Error creating event: " + str(error)}
        return {"weekday": weekday}

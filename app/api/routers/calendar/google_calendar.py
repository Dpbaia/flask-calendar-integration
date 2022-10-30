import datetime
import json
import os.path

import google.oauth2.credentials
import google_auth_oauthlib.flow
from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from icecream import ic
from marshmallow import fields
from pytz import timezone
from sqlalchemy.exc import ProgrammingError

from ...config.settings import config
from ...db.init_db import db
from ...models.token_storage import OauthStorage
from ...schemas.request_schema import RequestSchema
from ...schemas.response_schema import GoogleCalendarResponseSchema


class GoogleCalendar(MethodResource, Resource):
    @doc(
        description="List events for one month starting from the current date",
        tags=["Google", "Google Calendar"],
    )
    @marshal_with(GoogleCalendarResponseSchema)
    def get(self):
        (payload, day_of_the_week) = self.__build_freebusy_payload()
        credentials = OauthStorage.query.get(1)
        dictionary_credentials = credentials.__dict__
        del dictionary_credentials["_sa_instance_state"]
        del dictionary_credentials["id"]
        try:
            creds = google.oauth2.credentials.Credentials(**dictionary_credentials)
            service = build("calendar", "v3", credentials=creds)

            freebusy_result = service.freebusy().query(body=payload).execute()
            busy_times = (
                freebusy_result.get("calendars", {"primary": {"busy": []}})
                .get("primary", {"busy": []})
                .get("busy")
            )
            if not busy_times:
                return {}, 200
        except HttpError as error:
            return {"message": "Error retrieving busy times: " + str(error)}, 400

        info = {
            "busyTimes": busy_times,
            "weekday": day_of_the_week  # NOTE 0 - monday, 6 - sunday,
            # useful for building front-end of the calendar.
            # This is different from javascript, so keep in mind.
        }

        return info, 200

    @doc(description="Create an consultation time", tags=["Google", "Google Calendar"])
    @marshal_with(GoogleCalendarResponseSchema)
    def post(self):
        pass

    def __build_freebusy_payload(self):
        time = datetime.datetime.now(datetime.timezone.utc)
        brazil = timezone("America/Sao_Paulo")
        # Should catch edge cases such as summer time, someone checking around midnight, etc.
        brazil_time = time.astimezone(brazil)
        brazil_day = brazil_time.replace(hour=00, minute=00)
        in_30_days = (brazil_day + datetime.timedelta(days=30)).replace(
            hour=23, minute=59
        )
        return (
            {
                "timeMin": brazil_day.isoformat(),
                "timeMax": in_30_days.isoformat(),
                "items": [{"id": "primary"}],
            },
            brazil_day.weekday(),
        )


# class GoogleCalendarListDay(MethodResource, Resource):
#     @doc(description="List events for a specific day", tags=["Google", "Google Calendar"])
#     @marshal_with(GoogleAuthResponseSchema)


# class GoogleCalendarAddEvent(MethodResource, Resource):
#     @doc(description="List events for a specific day", tags=["Google", "Google Calendar"])
#     @marshal_with(GoogleAuthResponseSchema)


# def endpoint_example():
#     if "credentials" not in flask.session:
#         return flask.redirect("authorize")

#     # Load credentials from the session.
#     credentials = google.oauth2.credentials.Credentials(**flask.session["credentials"])

#     # get the response here
#     response = "call_to_google_api"

#     # Save credentials back to session in case access token was refreshed.
#     # ACTION ITEM: In a production app, you likely want to save these
#     #              credentials in a persistent database instead.
#     flask.session["credentials"] = credentials_to_dict(credentials)

#     return flask.jsonify(**response)


# def main():
#     """Shows basic usage of the Google Calendar API.
#     Prints the start and name of the next 10 events on the user's calendar.
#     """
#     # creds = authorization()
#     try:
#         service = build("calendar", "v3", credentials=creds)

#         # Call the Calendar API
#         now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
#         print("Getting the upcoming 10 events")
#         events_result = (
#             service.events()
#             .list(
#                 calendarId="primary",
#                 timeMin=now,
#                 maxResults=10,
#                 singleEvents=True,
#                 orderBy="startTime",
#             )
#             .execute()
#         )
#         events = events_result.get("items", [])

#         if not events:
#             print("No upcoming events found.")
#             return

#         # Prints the start and name of the next 10 events
#         for event in events:
#             start = event["start"].get("dateTime", event["start"].get("date"))
#             print(start, event["summary"])

#     except HttpError as error:
#         print("An error occurred: %s" % error)


# # if __name__ == "__main__":
# #     main()

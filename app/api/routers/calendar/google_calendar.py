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

from ...config.settings import config
from ...models.token_storage import OauthStorage
from ...schemas.request_schema import RequestDateSchema
from ...schemas.response_schema import GoogleCalendarResponseSchema

# TODO separate the google calendar controller from the front-end


class GoogleCalendar(MethodResource, Resource):
    @doc(
        description="List events for one month starting from the current date",
        tags=["Google", "Google Calendar"],
    )
    @use_kwargs(RequestDateSchema, location=("query"))
    @marshal_with(GoogleCalendarResponseSchema)
    def get(self, date=None):
        if date:
            info = self.__get_single_day_calendar(date)
        else:
            info = self.__get_thirty_days_calendar()
        return info, 200

    @doc(description="Create an consultation time", tags=["Google", "Google Calendar"])
    @marshal_with(GoogleCalendarResponseSchema)
    def post(self):
        pass

    def __get_single_day_calendar(self, date):
        brazil = timezone("America/Sao_Paulo")
        received_date = datetime.datetime.strptime(date, "%d-%m-%Y").replace(
            hour=00, minute=00, microsecond=30, tzinfo=brazil
        )
        end_of_day = received_date.replace(
            hour=23, minute=59, microsecond=30, tzinfo=brazil
        )
        info = GoogleCalendar().__get_google_calendar_response(
            payload={
                "timeMin": received_date.isoformat(),
                "timeMax": end_of_day.isoformat(),
                "items": [{"id": "primary"}],
            },
            day_of_the_week=received_date.weekday(),
        )
        return info

    def __get_brazil_time(self, time):
        brazil = timezone("America/Sao_Paulo")
        # Should catch edge cases such as summer time, someone checking around midnight, etc.
        brazil_time = time.astimezone(brazil)
        brazil_day = brazil_time.replace(hour=00, minute=00)
        return brazil_day

    def __get_thirty_days_calendar(self):
        time = datetime.datetime.now(datetime.timezone.utc)
        brazil_day = self.__get_brazil_time(time)
        in_30_days = (brazil_day + datetime.timedelta(days=30)).replace(
            hour=23, minute=59
        )
        info = self.__get_google_calendar_response(
            {
                "timeMin": brazil_day.isoformat(),
                "timeMax": in_30_days.isoformat(),
                "items": [{"id": "primary"}],
            },
            brazil_day.weekday(),
        )
        return info

    def __get_google_calendar_response(self, payload, day_of_the_week):
        credentials = OauthStorage.query.get(1)
        dictionary_credentials = credentials.__dict__
        del dictionary_credentials["_sa_instance_state"]
        del dictionary_credentials["id"]
        weekday_to_string_enum = {
            0: "Segunda",
            1: "Terça",
            2: "Quarta",
            3: "Quinta",
            4: "Sexta",
            5: "Sábado",
            6: "Domingo",
        }
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
                return {
                    "busyTimes": busy_times,
                    "weekday": weekday_to_string_enum[day_of_the_week],
                }  # TODO need to get the weekday in the empty response too!
        except HttpError as error:
            return {"message": "Error retrieving busy times: " + str(error)}
        return {
            "busyTimes": busy_times,
            "weekday": weekday_to_string_enum[day_of_the_week],
        }


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

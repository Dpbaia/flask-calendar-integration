import datetime

import google.oauth2.credentials
from flask_login import current_user
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pytz import timezone

from ..config.settings import config
from ..models.token_storage import OauthStorage


class GoogleCalendarsController:
    weekday_to_string_enum = {
        0: "Segunda",
        1: "Terça",
        2: "Quarta",
        3: "Quinta",
        4: "Sexta",
        5: "Sábado",
        6: "Domingo",
    }

    def get_single_day_calendar(self, date, user=False):
        brazil = timezone("America/Sao_Paulo")
        received_date = datetime.datetime.strptime(date, "%d-%m-%Y").replace(
            hour=00, minute=00, microsecond=30, tzinfo=brazil
        )
        end_of_day = received_date.replace(hour=23, minute=59, microsecond=30)
        info = self.__get_google_calendar_response(
            payload={
                "timeMin": received_date.isoformat(),
                "timeMax": end_of_day.isoformat(),
                "timeZone": "America/Sao_Paulo",
                "items": [{"id": "primary"}],
            },
            day_of_the_week=received_date.weekday(),
            user=user,
        )
        return info

    def get_thirty_days_calendar(self, user=None):
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
            user,
        )
        return info

    def get_google_authorization(self, user=None):
        if not user:
            credentials = OauthStorage.query.filter(
                OauthStorage.user_type == "admin"
            ).first()
        else:
            credentials = current_user
        dictionary_credentials = credentials.__dict__
        del dictionary_credentials["_sa_instance_state"]
        del dictionary_credentials["id"]
        del dictionary_credentials["user_type"]
        creds = google.oauth2.credentials.Credentials(**dictionary_credentials)
        return creds

    def create_event(self, creds, date, time, length, email):
        beginning_consultation = datetime.datetime.strptime(
            date + " " + time, "%d-%m-%Y %H:%M"
        )
        time = length.split(":")
        end_of_consultation = beginning_consultation + datetime.timedelta(
            hours=int(time[0]), minutes=int(time[1])
        )
        event = (
            {  # TODO fill out with the correct information provided by the professional
                "summary": "Consulta",
                "location": "",
                "description": "Consulta",
                "start": {
                    "dateTime": beginning_consultation.isoformat(),
                    "timeZone": "America/Sao_Paulo",
                },
                "end": {
                    "dateTime": end_of_consultation.isoformat(),
                    "timeZone": "America/Sao_Paulo",
                },
                "attendees": [
                    {"email": config["consultation_email"]},
                    {"email": email},
                ],
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email", "minutes": 24 * 60},
                        {"method": "popup", "minutes": 10},
                    ],
                },
            }
        )
        service = build("calendar", "v3", credentials=creds)
        service.events().insert(calendarId="primary", body=event).execute()
        return self.weekday_to_string_enum[end_of_consultation.weekday()]

    def __get_brazil_time(self, time):
        brazil = timezone("America/Sao_Paulo")
        # Should catch edge cases such as summer time, checking around midnight, etc.
        brazil_time = time.astimezone(brazil)
        brazil_day = brazil_time.replace(hour=00, minute=00)
        return brazil_day

    def __get_google_calendar_response(self, payload, day_of_the_week, user=False):
        try:
            creds = self.get_google_authorization(user)
        except HttpError as error:
            return {"message": "Error authenticating: " + str(error)}
        try:
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
                    "weekday": self.weekday_to_string_enum[day_of_the_week],
                }
        except HttpError as error:
            return {"message": "Error retrieving busy times: " + str(error)}
        return {
            "busyTimes": busy_times,
            "weekday": self.weekday_to_string_enum[day_of_the_week],
        }

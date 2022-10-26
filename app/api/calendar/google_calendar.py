from __future__ import print_function

import datetime
import os.path

import flask
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
from marshmallow import fields
from sqlalchemy.exc import ProgrammingError

from ..config.settings import config
from ..db.init_db import db
from ..models.token_storage import OauthStorage
from ..schemas.request_schema import RequestSchema
from ..schemas.response_schema import GoogleAuthResponseSchema

# TODO separate just oauth into its own file

# TODO separate router from the controller logic

# TODO need to store this in a safer place when deploying
CLIENT_SECRETS_FILE = (
    "app/api/calendar/credentials.json"  # TODO find way to substitute with the .env
)


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events.public.readonly",
    "https://www.googleapis.com/auth/calendar.events.owned",
    "https://www.googleapis.com/auth/calendar.freebusy",
]


def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }


class GoogleAuthorization(MethodResource, Resource):
    @doc(description="Authorize the google calendar app", tags=["Google"])
    @marshal_with(GoogleAuthResponseSchema)
    def get(self):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES
        )
        flow.redirect_uri = "http://127.0.0.1:5000/google/callback"  # TODO Change this to the front-end link when in development

        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type="offline",
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes="true",
        )
        flask.session["state"] = state
        return {
            "url": authorization_url,
            "message": "Generated authorization URL",
        }, 200


class GoogleCallback(MethodResource, Resource):
    @doc(description="Receive the credentials to be stored", tags=["Google"])
    @marshal_with(GoogleAuthResponseSchema)
    def get(self):
        db.create_all()
        # Specify the state when creating the flow in the callback so that it can
        # verified in the authorization server response.
        state = flask.session["state"]

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, state=state
        )
        flow.redirect_uri = flask.url_for(
            "googlecallback", _external=True
        )  # TODO change to the front-end url.

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = flask.request.url
        flow.fetch_token(authorization_response=authorization_response)

        # Store credentials in the session.
        # ACTION ITEM: In a production app, you likely want to save these
        #              credentials in a persistent database instead.
        credentials = flow.credentials
        try:
            "updating entry"
            storage = OauthStorage.query.get(1)
            if not storage:
                store_credentials = OauthStorage(**credentials_to_dict(credentials))
                db.session.add(store_credentials)
                db.session.commit()
            else:
                dict_credentials = credentials_to_dict(credentials)
                storage.token = dict_credentials.get("token")
                storage.refresh_token = dict_credentials.get("refresh_token")
                storage.token_uri = dict_credentials.get("token_uri")
                storage.client_id = dict_credentials.get("client_id")
                storage.client_secret = dict_credentials.get("client_secret")
                storage.scopes = dict_credentials.get("scopes")
                storage.expiry = dict_credentials.get("expiry")
                db.session.commit()
        except ProgrammingError as e:
            if e.code == "f405":
                store_credentials = OauthStorage(**credentials_to_dict(credentials))
                db.session.add(store_credentials)
                db.session.commit()
        except Exception as e:
            return {"message": "error: " + str(e)}, 400
        flask.session["credentials"] = credentials_to_dict(credentials)
        return {"message": "Stored credentials successfully"}, 201

        # @doc(description="Another POST API.", tags=["test"])
        # @use_kwargs(RequestSchema, location=("json"))
        # @marshal_with(ResponseSchema)  # marshalling
        # def post(self, api_type):
        #     """
        #     Get method represents a GET API method
        #     """
        #     return {"test": "My First Awesome API"}


def endpoint_example():
    if "credentials" not in flask.session:
        return flask.redirect("authorize")

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(**flask.session["credentials"])

    # get the response here
    response = "call_to_google_api"

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    flask.session["credentials"] = credentials_to_dict(credentials)

    return flask.jsonify(**response)


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    # creds = authorization()
    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

    except HttpError as error:
        print("An error occurred: %s" % error)


# if __name__ == "__main__":
#     main()

import json

import flask
import google_auth_oauthlib.flow
from flask_apispec import doc, marshal_with
from flask_apispec.views import MethodResource
from flask_restful import Resource
from sqlalchemy.exc import ProgrammingError

from ...config.settings import config
from ...db.db import db
from ...models.token_storage import OauthStorage
from ...schemas.response_schema import GoogleAuthResponseSchema

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events.public.readonly",
    "https://www.googleapis.com/auth/calendar.events.owned",
    "https://www.googleapis.com/auth/calendar.freebusy",
]

# TODO add scopes without public calendar and events.owned
# so that people can login with google and compare with their own events


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
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            json.loads(config["client_credentials"]), scopes=SCOPES
        )
        flow.redirect_uri = config["redirect_uri"]

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

        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            json.loads(config["client_credentials"]), scopes=SCOPES, state=state
        )

        # flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        #     CLIENT_SECRETS_FILE, scopes=SCOPES, state=state
        # )
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

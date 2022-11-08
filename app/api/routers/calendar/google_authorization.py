import json

import flask
import google_auth_oauthlib.flow
from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_login import current_user, login_required, login_user, logout_user
from flask_restful import Resource
from icecream import ic
from sqlalchemy.exc import ProgrammingError

from app.api.schemas.request_schema import RequestAdminId

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

SCOPES_PUBLIC = [
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
    @use_kwargs(RequestAdminId, location=("headers"))
    @marshal_with(GoogleAuthResponseSchema)
    def get(self, admin=None):
        current_scopes = SCOPES if admin == config["admin_key"] else SCOPES_PUBLIC
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            json.loads(config["client_credentials"]), scopes=current_scopes
        )
        flow.redirect_uri = (
            config["redirect_uri"]
            if admin == config["admin_key"]
            else config["public_redirect_uri"]
        )
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
        store_credentials = OauthStorage()
        try:
            storage = OauthStorage.query.filter(OauthStorage.user_type == "admin")
            if not storage.first():
                store_credentials = OauthStorage(
                    **(credentials_to_dict(credentials) | {"user_type": "admin"})
                )
                db.session.add(store_credentials)
                db.session.commit()
            else:
                store_credentials = storage.first()
                dict_credentials = credentials_to_dict(credentials)
                store_credentials.token = dict_credentials.get("token")
                store_credentials.refresh_token = dict_credentials.get("refresh_token")
                store_credentials.token_uri = dict_credentials.get("token_uri")
                store_credentials.client_id = dict_credentials.get("client_id")
                store_credentials.client_secret = dict_credentials.get("client_secret")
                store_credentials.scopes = dict_credentials.get("scopes")
                store_credentials.expiry = dict_credentials.get("expiry")
                db.session.commit()
        except ProgrammingError as e:
            if e.code == "f405":
                store_credentials = OauthStorage(**credentials_to_dict(credentials))
                db.session.add(store_credentials)
                db.session.commit()
        except Exception as e:
            return {"message": "error: " + str(e)}, 400
        login_user(store_credentials)
        return {"message": "Stored credentials successfully"}, 201


class GooglePublicCallback(MethodResource, Resource):
    @doc(description="Allows login from users", tags=["Google"])
    @marshal_with(GoogleAuthResponseSchema)
    def get(self):
        # Specify the state when creating the flow in the callback so that it can
        # verified in the authorization server response.
        state = flask.session["state"]
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            json.loads(config["client_credentials"]), scopes=SCOPES_PUBLIC, state=state
        )

        # flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        #     CLIENT_SECRETS_FILE, scopes=SCOPES, state=state
        # )
        flow.redirect_uri = flask.url_for(
            "googlepubliccallback", _external=True
        )  # TODO change to the front-end url.

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = flask.request.url
        flow.fetch_token(authorization_response=authorization_response)

        # Store credentials in the session.
        # ACTION ITEM: In a production app, you likely want to save these
        #              credentials in a persistent database instead.
        credentials = flow.credentials
        # dict_credentials = credentials_to_dict(credentials)
        # flask.session["credentials"] = dict_credentials
        user = OauthStorage(
            **(credentials_to_dict(credentials) | {"user_type": "public"})
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return {"message": "Logged in successfully."}, 200


class GoogleLogout(MethodResource, Resource):
    @doc(description="Allows users to log out", tags=["Google"])
    @marshal_with(GoogleAuthResponseSchema)
    @login_required
    def get(self):
        identification = current_user.id
        user_type = current_user.user_type
        logout_user()
        if user_type != "admin":
            ic("deleting user...")  # TODO replace with logging
            db.session.delete(OauthStorage.query.get(identification))
        flask.session.clear()
        return {"message": "Logged out successfully."}, 200

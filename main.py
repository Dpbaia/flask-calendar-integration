import datetime
import os

import flask_login
import pycron
import sentry_sdk
from flask import Flask
from flask_apispec.extension import FlaskApiSpec
from flask_cors import CORS
from flask_restful import Api
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.api.config.settings import config
from app.api.db.db import db, url
from app.api.models.token_storage import OauthStorage
from app.api.routers.calendar.google_authorization import (
    GoogleAuthorization,
    GoogleCallback,
    GoogleLogout,
    GooglePublicCallback,
)
from app.api.routers.calendar.google_calendar import GoogleCalendar

sentry_sdk.init(
    dsn=config["sentry"],
    integrations=[FlaskIntegration(), SqlalchemyIntegration()],
    traces_sample_rate=1.0,
)
login_manager = flask_login.LoginManager()


def create_app():
    app = Flask(__name__)
    login_manager.init_app(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = url
    db.init_app(app)

    api = Api(app)
    api.add_resource(GoogleAuthorization, "/google/authorization")
    api.add_resource(GoogleCallback, "/google/callback")
    api.add_resource(GooglePublicCallback, "/google/public-callback")
    api.add_resource(GoogleCalendar, "/google/consultation")
    api.add_resource(GoogleLogout, "/google/logout")

    @app.login_manager.user_loader
    def load_user(user_id):
        return OauthStorage.query.get(user_id)

    return app


if __name__ == "__main__":
    # When running locally, disable OAuthlib's HTTPs verification.
    # TODO ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    # TODO create cron to delete all but admin on db every saturday early
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    app = create_app()
    cors = CORS(app, resources={r"/*": {"origins": config["link_frontend"]}})

    docs = FlaskApiSpec(app)

    docs.register(GoogleAuthorization)
    docs.register(GoogleCallback)
    docs.register(GooglePublicCallback)
    docs.register(GoogleCalendar)
    docs.register(GoogleLogout)
    print("test")

    @pycron.cron("0 46 18 ? * SAT * ")
    async def test(timestamp: datetime):
        print(f"test cron job running at {timestamp}")

    app.secret_key = config["app_secret"]
    # TODO change to True when debugging
    app.run(debug=True)

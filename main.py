import os

import flask_login
import sentry_sdk
from flask import Flask, request
from flask_apispec.extension import FlaskApiSpec
from flask_cors import CORS
from flask_restful import Api
from markupsafe import escape
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

app = Flask(__name__)
login_manager.init_app(app)

app.config["SQLALCHEMY_DATABASE_URI"] = url
db.init_app(app)

api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": config["link_frontend"]}})
# TODO then do the user login auth (with google?) and apply to endpoints
# TODO maybe refactor this whole add resource and register to a loop?


api.add_resource(GoogleAuthorization, "/google/authorization")
api.add_resource(GoogleCallback, "/google/callback")
api.add_resource(GooglePublicCallback, "/google/public-callback")
api.add_resource(GoogleCalendar, "/google/consultation")
api.add_resource(GoogleLogout, "/google/logout")


docs = FlaskApiSpec(app)

docs.register(GoogleAuthorization)
docs.register(GoogleCallback)
docs.register(GooglePublicCallback)
docs.register(GoogleCalendar)
docs.register(GoogleLogout)


@app.route("/")
def hello():
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)}!"


@app.login_manager.user_loader
def load_user(user_id):
    return OauthStorage.query.get(user_id)


if __name__ == "__main__":
    # When running locally, disable OAuthlib's HTTPs verification.
    # TODO ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    app.secret_key = config["app_secret"]
    # TODO delete the debug when deploying
    app.run(debug=True)

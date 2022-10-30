import os

from flask import request
from flask_apispec.extension import FlaskApiSpec
from flask_cors import CORS
from flask_restful import Api
from markupsafe import escape

from app.api.config.settings import config
from app.api.db.init_db import app
from app.api.routers.calendar.google_authorization import (
    GoogleAuthorization,
    GoogleCallback,
)
from app.api.routers.calendar.google_calendar import GoogleCalendar
from app.api.routers.example import ExampleAPI, NewClass

api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": config["link_frontend"]}})
# TODO first do all google endpoints
# TODO then do the user login auth (with google?) and apply to endpoints
# TODO implement sentry monitoring
# TODO maybe refactor this whole add resource and register to a loop?

api.add_resource(ExampleAPI, "/awesome")
api.add_resource(NewClass, "/newclass")
api.add_resource(GoogleAuthorization, "/google/authorization")
api.add_resource(GoogleCallback, "/google/callback")
api.add_resource(GoogleCalendar, "/google/consultation")


docs = FlaskApiSpec(app)

docs.register(ExampleAPI)
docs.register(NewClass)
docs.register(GoogleAuthorization)
docs.register(GoogleCallback)
docs.register(GoogleCalendar)


@app.route("/")
def hello():
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)}!"


if __name__ == "__main__":
    # When running locally, disable OAuthlib's HTTPs verification.
    # TODO ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    app.secret_key = config["app_secret"]
    # TODO delete the debug when deploying
    app.run(debug=True)

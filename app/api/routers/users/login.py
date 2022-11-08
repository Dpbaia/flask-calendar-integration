import json
import os
import sqlite3

import requests
from db.db import db
from flask import Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient

from app.api.config.settings import config

# # create login endpoint
# class ExampleAPI(MethodResource, Resource):
#     @doc(description="Another POST API.", tags=["test"])
#     @use_kwargs(RequestSchema, location=("json"))
#     @marshal_with(ResponseSchema)  # marshalling
#     def post(self, api_type):
#         """
#         Get method represents a GET API method
#         """
#         return {"test": "My First Awesome API"}

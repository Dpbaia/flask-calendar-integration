from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import Column, Identity, Integer, String
from sqlalchemy.orm import validates

from app.api.db.db import db


class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer(), Identity(start=1), primary_key=True)
    name = Column(String(), nullable=False)
    email = db.Column(String(), nullable=False)

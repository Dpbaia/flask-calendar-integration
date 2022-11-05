from app.api.db.db import db
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import Column, Identity, Integer, String
from sqlalchemy.orm import validates

# class User(db.Model):
#     __tablename__ = "users"
#     id = Column(Integer(), Identity(start=1), primary_key=True)
#     username = Column(String(50), nullable=False)
#     password_hash = db.Column(db.String(128))

#     @validates("password_hash")
#     def validate_hash_password(self, key, password_hash):
#         password_hash = pwd_context.encrypt(password_hash)
#         return password_hash

#     def verify_password(self, password):
#         return pwd_context.verify(password, self.password_hash)

from sqlalchemy import ARRAY, Column, Identity, Integer, String

from app.api.db.db import db


class OauthStorage(db.Model):
    __tablename__ = "oauthstorage"
    id = Column(Integer(), Identity(start=1), primary_key=True)
    token = Column(String(1000))
    refresh_token = Column(String(1000))
    token_uri = Column(String(1000))
    client_id = Column(String(1000))
    client_secret = Column(String(1000))
    scopes = Column(ARRAY(String(300)))
    expiry = Column(String(1000))
    user_type = Column(String(6))

    def __repr__(self):
        return "<Id %r>" % self.id

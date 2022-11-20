import urllib.parse

from flask_sqlalchemy import SQLAlchemy

from app.api.config.settings import config

password = urllib.parse.quote_plus(config["db_password"])
name = config["db_user"]
host = config["db_host"]
port = config["db_port"]
db_name = config["db_name"]
# TODO change for deployment if url is different
url = f"postgresql://{name}:{password}@{host}:{port}/{db_name}"

db = SQLAlchemy()

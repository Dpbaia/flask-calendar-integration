import urllib.parse

from app.api.config.settings import config
from flask_sqlalchemy import SQLAlchemy

password = urllib.parse.quote_plus(config["db_password"])
name = config["db_user"]
host = config["db_host"]
port = config["db_port"]
db_name = config["db_name"]
# TODO will need to change this when deploying
url = f"postgresql://{name}:{password}@{host}:{port}/{db_name}"

db = SQLAlchemy()

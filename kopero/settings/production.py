from decouple import config
from .base import *
import dj_database_url


def dj_database_url_fix(db_config):
    db_config["HOST"] = (
        db_config["HOST"].replace("%3a", ":").replace("%3A", ":")
    )
    return db_config


DATABASES = {
    "default": dj_database_url_fix(
        dj_database_url.config(default=config("DATABASE_URL"))
    )
}

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())
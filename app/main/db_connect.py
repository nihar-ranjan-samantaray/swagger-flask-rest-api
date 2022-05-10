"""Config settings for for development, testing and production environments."""
import os
import sqlalchemy
import config

"""
from pathlib import Path
HERE = Path(__file__).parent
MYSQL_DEV = "sqlite:///" + str(HERE / "flask_api_tutorial_dev.db")
MYSQL_PROD = "sqlite:///" + str(HERE / "flask_api_tutorial_prod.db")
"""
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")

MYSQL_DEV = 'mysql://'+MYSQL_USER+':'+MYSQL_PASSWORD+'@'+MYSQL_HOST+':3306'
MYSQL_PROD = 'mysql://'+MYSQL_USER+':'+MYSQL_PASSWORD+'@'+MYSQL_HOST+':3306'

class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "open sesame")
    BCRYPT_LOG_ROUNDS = 4
    TOKEN_EXPIRE_HOURS = 0
    TOKEN_EXPIRE_MINUTES = 0
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SWAGGER_UI_DOC_EXPANSION = "list"
    RESTX_MASK_SWAGGER = False
    JSON_SORT_KEYS = False

class DevelopmentConfig(Config):
    """Development configuration."""

    TOKEN_EXPIRE_MINUTES = 15
    engine = sqlalchemy.create_engine(MYSQL_DEV)
    engine.execute("CREATE DATABASE IF NOT EXISTS "+MYSQL_DATABASE)
    engine.execute("USE "+MYSQL_DATABASE)
    SQLALCHEMY_DATABASE_URI = MYSQL_DEV+'/'+MYSQL_DATABASE


class ProductionConfig(Config):
    """Production configuration."""

    TOKEN_EXPIRE_HOURS = 1
    BCRYPT_LOG_ROUNDS = 13
    engine = sqlalchemy.create_engine(MYSQL_PROD)
    engine.execute("CREATE DATABASE IF NOT EXISTS "+MYSQL_DATABASE)
    engine.execute("USE "+MYSQL_DATABASE)
    SQLALCHEMY_DATABASE_URI = MYSQL_PROD+'/'+MYSQL_DATABASE
    PRESERVE_CONTEXT_ON_EXCEPTION = True


ENV_CONFIG_DICT = dict(
    development=DevelopmentConfig, production=ProductionConfig
)


def get_config(config_name):
    """Retrieve environment configuration settings."""
    return ENV_CONFIG_DICT.get(config_name, DevelopmentConfig)

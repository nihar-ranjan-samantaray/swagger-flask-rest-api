"""Config settings for for development, testing and production environments."""
import os
import sqlalchemy
import config

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_DATABASE = os.environ.get("POSTGRES_DATABASE")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

SQLITE_DEV = 'postgresql://'+POSTGRES_USER+':'+POSTGRES_PASSWORD+'@'+POSTGRES_HOST+':5432'+'/'+POSTGRES_DATABASE
# SQLITE_TEST = 'postgres://'+POSTGRES_USER+':'+POSTGRES_PASSWORD+'@'+POSTGRES_HOST+':5432'+'/'+POSTGRES_DATABASE
SQLITE_PROD = 'postgresql://'+POSTGRES_USER+':'+POSTGRES_PASSWORD+'@'+POSTGRES_HOST+':5432'+'/'+POSTGRES_DATABASE

class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "open sesame")
    BCRYPT_LOG_ROUNDS = 4
    TOKEN_EXPIRE_HOURS = 4320
    TOKEN_EXPIRE_MINUTES = 28800
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SWAGGER_UI_DOC_EXPANSION = "list"
    RESTX_MASK_SWAGGER = False
    JSON_SORT_KEYS = False


# class TestingConfig(Config):
#     """Testing configuration."""

#     TESTING = True
#     engine = sqlalchemy.create_engine(SQLITE_TEST)
#     SQLALCHEMY_DATABASE_URI = SQLITE_TEST


class DevelopmentConfig(Config):
    """Development configuration."""

    TOKEN_EXPIRE_HOURS = 4320
    TOKEN_EXPIRE_MINUTES = 28800
    engine = sqlalchemy.create_engine(SQLITE_DEV)
    SQLALCHEMY_DATABASE_URI = SQLITE_DEV


class ProductionConfig(Config):
    """Production configuration."""

    TOKEN_EXPIRE_HOURS = 4320
    TOKEN_EXPIRE_MINUTES = 28800
    BCRYPT_LOG_ROUNDS = 13
    engine = sqlalchemy.create_engine(SQLITE_PROD)
    SQLALCHEMY_DATABASE_URI = SQLITE_PROD
    PRESERVE_CONTEXT_ON_EXCEPTION = True


ENV_CONFIG_DICT = dict(
    development=DevelopmentConfig, production=ProductionConfig)


def get_config(config_name):
    """Retrieve environment configuration settings."""
    return ENV_CONFIG_DICT.get(config_name, DevelopmentConfig)

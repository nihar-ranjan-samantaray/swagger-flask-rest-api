"""Class definition for UTG Models."""
from datetime import datetime, timezone, timedelta
from uuid import uuid4

import jwt
from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property

from app.main import db, bcrypt
from app.main.util.datetime_util import (
    utc_now, get_local_utcoffset, make_tzaware, localized_dt_string, dtaware_fromtimestamp
    )
from app.main.util.result import Result


class BlacklistedToken(db.Model):
    """BlacklistedToken Model for storing JWT tokens."""
    __tablename__ = "token_blacklist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, default=utc_now)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token, expires_at):
        self.token = token
        self.expires_at = dtaware_fromtimestamp(expires_at, use_tz=timezone.utc)

    def __repr__(self):
        return f"<BlacklistToken token={self.token}>"

    @classmethod
    def check_blacklist(cls, token):
        exists = cls.query.filter_by(token=token).first()
        return True if exists else False

class User(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    registered_on = db.Column(db.DateTime, default=utc_now)


    @hybrid_property
    def registered_on_str(self):
        registered_on_utc = make_tzaware(
            self.registered_on, use_tz=timezone.utc, localize=False
        )
        return localized_dt_string(registered_on_utc, use_tz=get_local_utcoffset())
    @property
    def password(self):
        raise AttributeError("password: write-only field")

    @password.setter
    def password(self, password):
        log_rounds = current_app.config.get("BCRYPT_LOG_ROUNDS")
        hash_bytes = bcrypt.generate_password_hash(password, log_rounds)
        self.password_hash = hash_bytes.decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def encode_access_token(self):
        now = datetime.now(timezone.utc)
        token_age_h = current_app.config.get("TOKEN_EXPIRE_HOURS")
        token_age_m = current_app.config.get("TOKEN_EXPIRE_MINUTES")
        expire = now + timedelta(hours=token_age_h, minutes=token_age_m)
        if current_app.config["TESTING"]:
            expire = now + timedelta(seconds=5)
        payload = dict(exp=expire, iat=now, sub=self.user_id)
        key = current_app.config.get("SECRET_KEY")
        return jwt.encode(payload, key, algorithm="HS256")

    @staticmethod
    def decode_access_token(access_token):
        if isinstance(access_token, bytes):
            access_token = access_token.decode("ascii")
        if access_token.startswith("Bearer "):
            split = access_token.split("Bearer")
            access_token = split[1].strip()
        try:
            key = current_app.config.get("SECRET_KEY")
            payload = jwt.decode(access_token, key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            error = "Access token expired. Please log in again."
            return Result.Fail(error)
        except jwt.InvalidTokenError:
            error = "Invalid token. Please log in again."
            return Result.Fail(error)

        if BlacklistedToken.check_blacklist(access_token):
            error = "Token blacklisted. Please log in again."
            return Result.Fail(error)
        user_dict = dict(
            user_id=payload["sub"],
            token=access_token,
            expires_at=payload["exp"],
        )
        return Result.Ok(user_dict)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

class ExtractedItems(db.Model):
    __tablename__ = "extracted_items"

    extraction_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(30), db.ForeignKey('user.username', ondelete="CASCADE"))
    job_number = db.Column(db.Integer)
    task_item_number = db.Column(db.String(20))
    task_quantity = db.Column(db.Integer)
    extracted_ts = db.Column(db.DateTime, nullable=True)

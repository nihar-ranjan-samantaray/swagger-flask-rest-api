"""API blueprint configuration."""
from flask import Blueprint
from flask_restx import Api

from app.main.controller.controller import app_ns

api_bp = Blueprint("api", __name__)
authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(
    api_bp,
    version="2.0",
    title="Flask API of Thbred",
    description="Welcome to the Swagger UI of Flask API",
    # security="Bearer",
    # doc="/",
    authorizations=authorizations,
)

api.add_namespace(app_ns, path="")

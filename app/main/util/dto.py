"""Parsers and serializers for UTG API endpoints."""
from flask_restx import Model
from flask_restx.fields import String, Boolean, Integer
from flask_restx.inputs import email
from flask_restx.reqparse import RequestParser
import werkzeug

registerUser_reqparser = RequestParser(bundle_errors=True)
login_reqparser = RequestParser(bundle_errors=True)
resetPassword_reqparser = RequestParser(bundle_errors=True)
extractPDF_reqparser = RequestParser(bundle_errors=True)
fetchExtractedItems_reqparser = RequestParser(bundle_errors=True)
updateExtractedItems_reqparser = RequestParser(bundle_errors=True)

registerUser_reqparser.add_argument(name="username", type=str, location="form", required=True, nullable=False)
registerUser_reqparser.add_argument(name="email", type=email(), location="form", required=False, nullable=True)
registerUser_reqparser.add_argument(name="password", type=str, location="form", required=True, nullable=False)

login_reqparser.add_argument(name="username", type=str, location="form", required=True, nullable=False)
login_reqparser.add_argument(name="password", type=str, location="form", required=True, nullable=False)

resetPassword_reqparser.add_argument(name="password", type=str, location="form", required=True, nullable=False)

extractPDF_reqparser.add_argument(name="files", type=werkzeug.datastructures.FileStorage, location='files', required=True, nullable=False)

fetchExtractedItems_reqparser.add_argument(name="id", type=int, location="form", required=True, nullable=False)

updateExtractedItems_reqparser.add_argument(name="id", type=int, location="form", required=True, nullable=False)
updateExtractedItems_reqparser.add_argument(name="job_number", type=int, location="form", required=True, nullable=False)
updateExtractedItems_reqparser.add_argument(name="task_item_number", type=str, location="form", required=True, nullable=False)
updateExtractedItems_reqparser.add_argument(name="task_quantity", type=int, location="form", required=True, nullable=False)

user_model = Model(
    "User",
    {
        "user_id": Integer,
        "username": String,
        "email": String,
        "registered_on": String(attribute="registered_on_str"),
        "token_expires_in": String,
    },
)
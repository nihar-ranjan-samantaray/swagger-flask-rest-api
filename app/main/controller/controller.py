"""API endpoint definitions for /auth namespace."""
from http import HTTPStatus
from flask_restx import Namespace, Resource

from app.main.util.dto import (
    user_model, registerUser_reqparser, login_reqparser, resetPassword_reqparser, extractPDF_reqparser, fetchExtractedItems_reqparser, updateExtractedItems_reqparser
)
from app.main.service.service import (
    registerUser, login, logout, get_logged_in_user, resetPassword, extractPDF, fetchExtractedItems, updateExtractedItems,
)

app_ns = Namespace(name="", validate=True)
app_ns.models[user_model.name] = user_model

@app_ns.route("/registerUser", endpoint="register_user")
class RegisterUser(Resource):
    @app_ns.expect(registerUser_reqparser)
    @app_ns.response(int(HTTPStatus.OK), "User Registered Successfully")
    @app_ns.response(int(HTTPStatus.CONFLICT), "Username is already registered.")
    @app_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """ Add username, email and password to register a user """
        request_data = registerUser_reqparser.parse_args()
        username = request_data.get("username")
        email = request_data.get("email")
        password = request_data.get("password")
        return registerUser(username, email, password)

@app_ns.route("/login", endpoint="login")
class LoginUser(Resource):
    @app_ns.expect(login_reqparser)
    @app_ns.response(int(HTTPStatus.OK), "Login succeeded.")
    @app_ns.response(int(HTTPStatus.UNAUTHORIZED), "username or password does not match")
    @app_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Authenticate an existing user and return an access token."""
        request_data = login_reqparser.parse_args()
        username = request_data.get("username")
        password = request_data.get("password")
        return login(username, password)

@app_ns.route("/userInfo", endpoint="user_info")
class UserInfo(Resource):
    @app_ns.doc(security="Bearer")
    @app_ns.response(int(HTTPStatus.OK), "Token is currently valid.", user_model)
    @app_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @app_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @app_ns.marshal_with(user_model)
    def get(self):
        """Validate access token and return user info."""
        return get_logged_in_user()

@app_ns.route("/logout", endpoint="logout")
class LogoutUser(Resource):
    @app_ns.doc(security="Bearer")
    @app_ns.response(int(HTTPStatus.OK), "Log out succeeded, token is no longer valid.")
    @app_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @app_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Add token to blacklist, deauthenticating the current user."""
        return logout()

@app_ns.route("/resetPassword", endpoint="reset_password")
class ResetPassword(Resource):
    @app_ns.doc(security="Bearer")
    @app_ns.expect(resetPassword_reqparser)
    @app_ns.response(int(HTTPStatus.OK), "Password Changed Successfully")
    @app_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """ Enter new password to update for the user """
        request_data = resetPassword_reqparser.parse_args()
        password = request_data.get("password")
        return resetPassword(password)
 
@app_ns.route("/extractPDF", endpoint="extract_PDF")    
class ExtractPDF(Resource):
    @app_ns.doc(security="Bearer") 
    @app_ns.expect(extractPDF_reqparser) 
    @app_ns.response(int(HTTPStatus.CREATED), "PDF Extracted Successfully")
    @app_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    def post(self):
        """ Upload PDF for Extraction"""
        request_data = extractPDF_reqparser.parse_args()
        files = request_data.get("files")
        return extractPDF(files)

@app_ns.route("/fetchExtractedItems", endpoint="fetch_extracted_items")
class FetchExtractedItems(Resource):
    @app_ns.doc(security="Bearer")
    @app_ns.expect(fetchExtractedItems_reqparser)
    @app_ns.response(int(HTTPStatus.OK), "Extracted Items Fetched Successfully")
    @app_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """ Fetch Data from Extracted Items Table """
        request_data = fetchExtractedItems_reqparser.parse_args()
        id = request_data.get("id")
        return fetchExtractedItems(id)


@app_ns.route("/updateExtractedItems", endpoint="update_extracted_items")
class UpdateExtractedItems(Resource):
    @app_ns.doc(security="Bearer")
    @app_ns.expect(updateExtractedItems_reqparser)
    @app_ns.response(int(HTTPStatus.OK), "Extracted Items Updated Successfully")
    @app_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def put(self):
        """ Update Extracted Items Table Data """
        request_data = updateExtractedItems_reqparser.parse_args()
        id = request_data.get("id")
        job_number = request_data.get("job_number")
        task_item_number = request_data.get("task_item_number")
        task_quantity = request_data.get("task_quantity")
        return updateExtractedItems(id, job_number, task_item_number, task_quantity)
 
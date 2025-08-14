from flask import Blueprint, request, jsonify
from flask.views import MethodView
from pydantic import ValidationError
from ..models import Login, ErrorResponse
from ..services.auth_service import login, logout
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


class RegisterAPI(MethodView):
    # TODO: Not implemented yet
    def post(self):
        """
        Register a new account.
        Different from patient POST as this is meant for patients registering.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = PatientCreate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400

        try:
            result = add_patient(data)
            return jsonify(result["data"].model_dump()), 201
        except ForeignKeyViolation as fk:
            error_response = ErrorResponse(
                error="Invalid foreign key reference.")
            return jsonify(error_response.model_dump()), 400
        except Exception as e:
            error_response = ErrorResponse(error=str(e))
            return jsonify(error_response.model_dump()), 500


class LoginAPI(MethodView):
    def post(self):
        """
        Check user login credentials and return JWT token.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = Login.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400

        try:
            response_data, response_code = login(data)
            return jsonify(response_data), response_code
        except Exception as e:
            return jsonify({"status": "Internal server error", "error": str(e)}), 500


class LogoutAPI(MethodView):
    @jwt_required()
    def post(self):
        try:
            jwt_data = get_jwt()
            jti = jwt_data["jti"]
            user_id = get_jwt_identity()

            exp_timestamp = jwt_data["exp"]
            expires_at = datetime.fromtimestamp(exp_timestamp)

            response_data, status_code = logout(jti, user_id, expires_at)
            return jsonify(response_data), status_code

        except Exception as e:
            error_response = ErrorResponse(error=str(e))
            return jsonify(error_response.model_dump()), 500


auth_register_view = RegisterAPI.as_view('register_account')
auth_bp.add_url_rule(
    '/register', view_func=auth_register_view, methods=['POST'])

auth_login_view = LoginAPI.as_view('login')
auth_bp.add_url_rule('/login', view_func=auth_login_view, methods=['POST'])

auth_logout_view = LogoutAPI.as_view('logout')
auth_bp.add_url_rule('/logout', view_func=auth_logout_view, methods=['POST'])

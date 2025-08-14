from flask import Blueprint, request, jsonify
from flask.views import MethodView
from pydantic import ValidationError
from ..models import CredentialsUpdate, UserCreate, ErrorResponse, UserUpdate, StatusResponse
from ..services.users_service import add_user, get_user, update_user, hide_user, update_user_credentials
from ..utils.auth_utils import roles_required, self_user_doctor_or_admin_access

users_bp = Blueprint('users', __name__)


class UserPostAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def post(self):
        """
        Add a new user.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = UserCreate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400

        try:
            response_result, _ = add_user(data)
            return jsonify(response_result["data"].model_dump()), 201
        except Exception as e:
            error_response = ErrorResponse(error=repr(e))
            return jsonify(error_response.model_dump()), 500


class UserPutAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def put(self, user_id: str):
        """
        Modify the information of an user while still keeping the old version in history.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = UserUpdate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400
        try:
            response_result, _ = update_user(user_id, data)
            return jsonify(response_result["data"].model_dump()), 201
        except Exception as e:
            error_response = ErrorResponse(error=str(e))
            return jsonify(error_response.model_dump()), 500


class UserGetAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def get(self, user_id: str):
        """
        Retrieve an user by their user_id, including user info.
        """
        result, status_code = get_user(user_id)
        if status_code == 200:
            return jsonify(result["data"].model_dump()), 200
        elif status_code == 404:
            error_response = ErrorResponse(error=result["message"])
            return jsonify(error_response.model_dump()), 404
        else:
            error_response = ErrorResponse(error=result["message"])
            return jsonify(error_response.model_dump()), 500


class UserDeleteAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def delete(self, user_id: str):
        """
        Act as if deleting the information of an user by making it hidden.
        """
        result, status_code = hide_user(user_id)
        if status_code == 200:
            success_response = StatusResponse(status=result["status"])
            return jsonify(success_response.model_dump()), status_code
        else:
            error_response = ErrorResponse(error=result["error"])
            return jsonify(error_response.model_dump()), status_code


class UserPutCredentialsAPI(MethodView):
    @self_user_doctor_or_admin_access(param_name='user_id')
    def put(self, user_id: str):
        """
        Modify the information of an user while still keeping the old version in history.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = CredentialsUpdate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400
        result, status_code = update_user_credentials(user_id, data)
        if status_code == 201:
            status_response = StatusResponse(status=result["status"])
            return jsonify(status_response.model_dump()), status_code
        else:
            error_response = ErrorResponse(error=result["error"])
            return jsonify(error_response.model_dump()), status_code


users_post_view = UserPostAPI.as_view('add_user')
users_bp.add_url_rule('', view_func=users_post_view, methods=['POST'])

users_put_view = UserPutAPI.as_view('update_user')
users_bp.add_url_rule('/<user_id>',
                      view_func=users_put_view, methods=['PUT'])

users_put_credentials_view = UserPutCredentialsAPI.as_view(
    'update_user_credentials')
users_bp.add_url_rule('/<user_id>/credentials',
                      view_func=users_put_credentials_view, methods=['PUT'])

users_get_view = UserGetAPI.as_view('get_user')
users_bp.add_url_rule('/<user_id>',
                      view_func=users_get_view, methods=['GET'])

users_delete_view = UserDeleteAPI.as_view('delete_user')
users_bp.add_url_rule('/<user_id>',
                      view_func=users_delete_view, methods=['DELETE'])

from flask import Blueprint, request, jsonify
from flask.views import MethodView
from pydantic import ValidationError
from ..models import CoordinateCreate, CoordinateUpdate, ErrorResponse, StatusResponse, EmailPhoneUpdate
from ..services.coordinate_service import add_coordinates, update_coordinates, hide_coordinates, update_email_phone
from ..utils.auth_utils import roles_required, self_user_doctor_or_admin_access

coordinates_bp = Blueprint('coordinates', __name__)


class CoordinatesPostAPI(MethodView):
    @self_user_doctor_or_admin_access(param_name='user_id')
    def post(self, user_id: str):
        """
        Add a new user coordinates.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = CoordinateCreate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400

        response_result, response_code = add_coordinates(
            user_id, data)
        if response_code == 201:
            return jsonify(response_result["message"].model_dump()), response_code
        else:
            error_response = ErrorResponse(
                error=repr(response_result["message"]))
            return jsonify(error_response.model_dump()), response_code


class CoordinatesPutAPI(MethodView):
    @self_user_doctor_or_admin_access(param_name='user_id')
    def put(self, coordinate_id: str):
        """
        Modify the information of user coordinates while still keeping the old version in history.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = CoordinateUpdate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400
        try:
            response_result, _ = update_coordinates(coordinate_id, data)
            return jsonify(response_result["data"].model_dump()), 201
        except Exception as e:
            error_response = ErrorResponse(error=str(e))
            return jsonify(error_response.model_dump()), 500


class CoordinatesPutAltAPI(MethodView):
    @self_user_doctor_or_admin_access(param_name='user_id')
    def put(self, user_id: str, coordinate_id: str):
        """
        Modify the information of user coordinates while still keeping the old version in history.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = CoordinateUpdate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400
        try:
            response_result, _ = update_coordinates(coordinate_id, data)
            return jsonify(response_result["data"].model_dump()), 201
        except Exception as e:
            error_response = ErrorResponse(error=str(e))
            return jsonify(error_response.model_dump()), 500


class EmailPhonePutAPI(MethodView):
    @self_user_doctor_or_admin_access(param_name='user_id')
    def put(self, user_id: str):
        """
        Modify the information of user phone number or email while still keeping the old version in history.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = EmailPhoneUpdate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400
        try:
            response_result, _ = update_email_phone(user_id, data)
            return jsonify(response_result["data"].model_dump()), 201
        except Exception as e:
            error_response = ErrorResponse(error=str(e))
            return jsonify(error_response.model_dump()), 500


class CoordinatesDeleteAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def delete(self, coordinate_id: str):
        """
        Act as if deleting the information of a history by making it hidden.
        """
        result, status_code = hide_coordinates(coordinate_id)
        if status_code == 200:
            success_response = StatusResponse(status=result["status"])
            return jsonify(success_response.model_dump()), status_code
        else:
            error_response = ErrorResponse(error=result["error"])
            return jsonify(error_response.model_dump()), status_code


coordinates_post_view = CoordinatesPostAPI.as_view('add_coordinates')
coordinates_bp.add_url_rule('/users/<user_id>/coordinates',
                            view_func=coordinates_post_view, methods=['POST'])

coordinates_put_view = CoordinatesPutAPI.as_view('update_coordinates')
coordinates_bp.add_url_rule('/coordinates/<coordinate_id>',
                            view_func=coordinates_put_view, methods=['PUT'])

coordinates_put_alt_view = CoordinatesPutAltAPI.as_view(
    'update_coordinates_alt')
coordinates_bp.add_url_rule('/users/<user_id>/coordinates/<coordinate_id>',
                            view_func=coordinates_put_alt_view, methods=['PUT'])

coordinates_delete_view = CoordinatesDeleteAPI.as_view('delete_coordinates')
coordinates_bp.add_url_rule('/coordinates/<coordinate_id>',
                            view_func=coordinates_delete_view, methods=['DELETE'])


email_phone_put_view = EmailPhonePutAPI.as_view('update_email_phone')
coordinates_bp.add_url_rule('/users/<user_id>/coordinates/email-phone',
                            view_func=email_phone_put_view, methods=['PUT'])

from flask import Blueprint, request, jsonify
from flask.views import MethodView
from pydantic import ValidationError
from ..models import HistoryCreate, HistoryUpdate, ErrorResponse, StatusResponse
from ..services.history_service import add_history, update_history, hide_history
from ..utils.auth_utils import roles_required

history_bp = Blueprint('medical_history', __name__)


class MedicalHistoryPostAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def post(self, medical_insurance_id: str):
        """
        Add a new patient medical history.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = HistoryCreate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400

        try:
            response_result, response_code = add_history(
                medical_insurance_id, data)
            if response_code == 400:
                error_response = ErrorResponse(
                    error=repr(response_result["message"]))
                return jsonify(error_response.model_dump()), 400
            return jsonify(response_result["message"].model_dump()), response_code
        except Exception as e:
            error_response = ErrorResponse(error=repr(e))
            return jsonify(error_response.model_dump()), 500


class MedicalHistoryPutAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def put(self, medical_insurance_id: str, history_id: str):
        """
        Modify the information of patient medical history while still keeping the old version in history.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = HistoryUpdate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400
        try:
            response_result, _ = update_history(history_id, data)
            return jsonify(response_result["data"].model_dump()), 201
        except Exception as e:
            error_response = ErrorResponse(error=str(e))
            return jsonify(error_response.model_dump()), 500


class MedicalHistoryPutAltAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def put(self, history_id: str):
        """
        Modify the information of patient medical history while still keeping the old version in history.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = HistoryUpdate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400
        try:
            response_result, _ = update_history(history_id, data)
            return jsonify(response_result["data"].model_dump()), 201
        except Exception as e:
            error_response = ErrorResponse(error=str(e))
            return jsonify(error_response.model_dump()), 500


class MedicalHistoryDeleteAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def delete(self, history_id: str):
        """
        Act as if deleting the information of a history by making it hidden.
        """
        result, status_code = hide_history(history_id)
        if status_code == 200:
            success_response = StatusResponse(status=result["status"])
            return jsonify(success_response.model_dump()), status_code
        else:
            error_response = ErrorResponse(error=result["error"])
            return jsonify(error_response.model_dump()), status_code


history_post_view = MedicalHistoryPostAPI.as_view('add_history')
history_bp.add_url_rule('/patients/<medical_insurance_id>/history',
                        view_func=history_post_view, methods=['POST'])

history_put_view = MedicalHistoryPutAPI.as_view('update_history')
history_bp.add_url_rule('/patients/<medical_insurance_id>/history/<history_id>',
                        view_func=history_put_view, methods=['PUT'])

history_put_alt_view = MedicalHistoryPutAltAPI.as_view('update_history_alt')
history_bp.add_url_rule('/history/<history_id>',
                        view_func=history_put_alt_view, methods=['PUT'])

history_delete_view = MedicalHistoryDeleteAPI.as_view('delete_history')
history_bp.add_url_rule('/history/<history_id>',
                        view_func=history_delete_view, methods=['DELETE'])

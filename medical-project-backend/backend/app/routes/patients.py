from ..utils.auth_utils import roles_required, self_doctor_or_admin_access
from flask import Blueprint, request, jsonify
from flask.views import MethodView
from pydantic import ValidationError
from ..models import PatientCreate, ErrorResponse, PatientUpdate, StatusResponse, PatientVersionHistoryResponse
from ..services.patient_service import add_patient, get_patient, update_patient, hide_patient, get_patient_at_date, get_patient_version_history
from datetime import datetime

patients_bp = Blueprint('patients', __name__)


class PatientAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def post(self):
        """
        Add a new patient along with their user info and coordinates.
        Optionally, establish parent-child relationships.
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
            response_result, _ = add_patient(data)
            return jsonify(response_result["data"].model_dump()), 201
        except Exception as e:
            error_response = ErrorResponse(error=repr(e))
            return jsonify(error_response.model_dump()), 500


class PatientPutAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def put(self, medical_insurance_id: str):
        """
        Modify the information of patient while still keeping the old version in history.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = PatientUpdate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400
        try:
            response_result, _ = update_patient(medical_insurance_id, data)
            return jsonify(response_result["data"].model_dump()), 201
        except Exception as e:
            error_response = ErrorResponse(error=str(e))
            return jsonify(error_response.model_dump()), 500


class PatientDetailAPI(MethodView):
    @self_doctor_or_admin_access(param_name='medical_insurance_id')
    def get(self, medical_insurance_id: str):
        """
        Retrieve a patient by their medical_insurance_id, including user info,
        multiple coordinates, medical history, medical visits, and parents.
        """
        from_date_str = request.args.get('from_date')
        if from_date_str:
            try:
                from_date = datetime.strptime(from_date_str, '%d-%m-%Y').date()
            except Exception as e:
                error_response = ErrorResponse(error=str(e))
                return jsonify(error_response.model_dump()), 400
            result, status_code = get_patient_at_date(
                medical_insurance_id, from_date)
        else:
            result, status_code = get_patient(medical_insurance_id)
        if status_code == 200:
            return jsonify(result["data"].model_dump()), 200
        elif status_code == 404:
            error_response = ErrorResponse(error=result["message"])
            return jsonify(error_response.model_dump()), 404
        else:
            error_response = ErrorResponse(error=result["message"])
            return jsonify(error_response.model_dump()), 500


class PatientDeleteAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def delete(self, medical_insurance_id: str):
        """
        Act as if deleting the information of a patient by making it hidden.
        """
        result, status_code = hide_patient(medical_insurance_id)
        if status_code == 200:
            success_response = StatusResponse(status=result["status"])
            return jsonify(success_response.model_dump()), status_code
        else:
            error_response = ErrorResponse(error=result["error"])
            return jsonify(error_response.model_dump()), status_code


class PatientHistoryAPI(MethodView):
    @self_doctor_or_admin_access(param_name='medical_insurance_id')
    def get(self, medical_insurance_id: str):
        """
        Retrieve the complete version history of a patient by their medical_insurance_id.
        Returns a map where each key is a timestamp and the value is the full patient record at that time.
        """
        result, status_code = get_patient_version_history(medical_insurance_id)
        if status_code == 200:
            return jsonify(result["data"]), 200
        elif status_code == 404:
            error_response = ErrorResponse(error=result["message"])
            return jsonify(error_response.model_dump()), 404
        else:
            error_response = ErrorResponse(error=str(result["message"]))
            return jsonify(error_response.model_dump()), 500


patients_view = PatientAPI.as_view('add_patient')
patients_bp.add_url_rule('', view_func=patients_view, methods=['POST'])

patients_put_view = PatientPutAPI.as_view('update_patient')
patients_bp.add_url_rule('/<medical_insurance_id>',
                         view_func=patients_put_view, methods=['PUT'])

patient_detail_view = PatientDetailAPI.as_view('get_patient')
patients_bp.add_url_rule('/<medical_insurance_id>',
                         view_func=patient_detail_view, methods=['GET'])

patient_delete_view = PatientDeleteAPI.as_view('delete_patient')
patients_bp.add_url_rule('/<medical_insurance_id>',
                         view_func=patient_delete_view, methods=['DELETE'])

patient_history_view = PatientHistoryAPI.as_view('get_patient_history')
patients_bp.add_url_rule('/<medical_insurance_id>/version_history',
                         view_func=patient_history_view, methods=['GET'])

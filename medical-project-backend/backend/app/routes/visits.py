from flask import Blueprint, request, jsonify
from flask.views import MethodView
from pydantic import ValidationError
from ..models import VisitCreate, VisitUpdate, ErrorResponse, StatusResponse
from ..services.visit_service import add_visit, update_visit, hide_visit
from ..utils.auth_utils import roles_required

visits_bp = Blueprint('medical_visits', __name__)


class MedicalVisitPostAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def post(self, medical_insurance_id: str):
        """
        Add a new patient medical visits.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = VisitCreate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400

        try:
            response_result, response_code = add_visit(
                medical_insurance_id, data)
            if response_code == 400:
                error_response = ErrorResponse(
                    error=repr(response_result["message"]))
                return jsonify(error_response.model_dump()), 400
            return jsonify(response_result["message"].model_dump()), response_code
        except Exception as e:
            error_response = ErrorResponse(error=repr(e))
            return jsonify(error_response.model_dump()), 500


class MedicalVisitPutAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def put(self, medical_insurance_id: str, visit_id: str):
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
            data = VisitUpdate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400
        try:
            response_result, _ = update_visit(visit_id, data)
            return jsonify(response_result["data"].model_dump()), 201
        except Exception as e:
            error_response = ErrorResponse(error=str(e))
            return jsonify(error_response.model_dump()), 500


class MedicalVisitPutAltAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def put(self, visit_id: str):
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
            data = VisitUpdate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400
        try:
            response_result, _ = update_visit(visit_id, data)
            return jsonify(response_result["data"].model_dump()), 201
        except Exception as e:
            error_response = ErrorResponse(error=str(e))
            return jsonify(error_response.model_dump()), 500


class MedicalVisitDeleteAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def delete(self, visit_id: str):
        """
        Act as if deleting the information of a visit by making it hidden.
        """
        result, status_code = hide_visit(visit_id)
        if status_code == 200:
            success_response = StatusResponse(status=result["status"])
            return jsonify(success_response.model_dump()), status_code
        else:
            error_response = ErrorResponse(error=result["error"])
            return jsonify(error_response.model_dump()), status_code


visit_post_view = MedicalVisitPostAPI.as_view('add_visit')
visits_bp.add_url_rule('/patients/<medical_insurance_id>/visits',
                       view_func=visit_post_view, methods=['POST'])

visit_put_view = MedicalVisitPutAPI.as_view('update_visit')
visits_bp.add_url_rule('/patients/<medical_insurance_id>/visits/<visit_id>',
                       view_func=visit_put_view, methods=['PUT'])

visit_put_alt_view = MedicalVisitPutAltAPI.as_view('update_visit_alt')
visits_bp.add_url_rule('/visits/<visit_id>',
                       view_func=visit_put_alt_view, methods=['PUT'])

visit_delete_view = MedicalVisitDeleteAPI.as_view('delete_visit')
visits_bp.add_url_rule('/visits/<visit_id>',
                       view_func=visit_delete_view, methods=['DELETE'])

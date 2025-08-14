from flask import Blueprint, jsonify
from flask.views import MethodView
from ..services.establishment_service import get_all_establishments, hide_establishment
from ..utils.auth_utils import roles_required
from ..models import ErrorResponse, StatusResponse

establishments_bp = Blueprint('establishments', __name__)


class EstablishmentsAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def get(self):
        """
        Retrieve all establishments.
        """
        result, status_code = get_all_establishments()
        if status_code == 200:
            return jsonify(result), 200
        else:
            return jsonify(result), status_code


class EstablishmentsDeleteAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def delete(self, establishment_id: str):
        """
        Act as if deleting the information of a patient by making it hidden.
        """
        result, status_code = hide_establishment(establishment_id)
        if status_code == 200:
            status_response = StatusResponse(status=result["status"])
            return jsonify(status_response.model_dump()), 200
        else:
            error_response = ErrorResponse(error=result["error"])
            return jsonify(error_response.model_dump()), status_code


establishments_view = EstablishmentsAPI.as_view('get_establishments')
establishments_bp.add_url_rule(
    '', view_func=establishments_view, methods=['GET'])

establishments_hide_view = EstablishmentsDeleteAPI.as_view(
    'hide_establishments')
establishments_bp.add_url_rule(
    '/<establishment_id>', view_func=establishments_hide_view, methods=['DELETE'])

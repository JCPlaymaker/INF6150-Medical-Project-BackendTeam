from flask import Blueprint, jsonify
from flask.views import MethodView
from ..services.doctor_service import get_all_doctors
from ..utils.auth_utils import roles_required

doctors_bp = Blueprint('doctors', __name__)


class DoctorsAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def get(self):
        """
        Retrieve all doctors.
        """
        result, status_code = get_all_doctors()
        if status_code == 200:
            return jsonify(result), 200
        else:
            return jsonify(result), status_code


doctors_view = DoctorsAPI.as_view('get_doctors')
doctors_bp.add_url_rule('', view_func=doctors_view, methods=['GET'])

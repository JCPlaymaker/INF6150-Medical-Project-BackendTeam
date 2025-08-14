from flask import Blueprint, jsonify, request
from flask.views import MethodView
from ..models import ErrorResponse, ParentCreate, StatusResponse, UserCreateResponse
from ..services.parents_service import add_parents, hide_parents, add_parents_alt
from ..utils.auth_utils import roles_required
from pydantic import ValidationError

parents_bp = Blueprint('parents', __name__)


class ParentsPostAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def post(self, child_user_id: str, parent_user_id: str):
        """
        Add a new user parent relationship.
        """
        result, status_code = add_parents(
            child_user_id, parent_user_id)
        if status_code == 201:
            success_response = StatusResponse(status=result["status"])
            return jsonify(success_response.model_dump()), status_code
        else:
            error_response = ErrorResponse(error=result["error"])
            return jsonify(error_response.model_dump()), status_code


class ParentsPostAltAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def post(self, child_user_id: str):
        """
        Add a new user parent relationship.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])
            data = ParentCreate.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400

        result, status_code = add_parents_alt(
            child_user_id, data)
        if status_code == 201:
            success_response = UserCreateResponse(user_id=result["user_id"])
            return jsonify(success_response.model_dump()), status_code
        else:
            error_response = ErrorResponse(error=result["error"])
            return jsonify(error_response.model_dump()), status_code


class ParentsDeleteAPI(MethodView):
    @roles_required(["ADMIN", "DOCTOR", "HEALTHCARE PROFESSIONAL"])
    def delete(self, child_user_id: str, parent_user_id: str):
        """
        Act as if deleting the information of a parent relationship by making it hidden.
        """
        result, status_code = hide_parents(child_user_id, parent_user_id)
        if status_code == 200:
            success_response = StatusResponse(status=result["status"])
            return jsonify(success_response.model_dump()), status_code
        else:
            error_response = ErrorResponse(error=result["error"])
            return jsonify(error_response.model_dump()), status_code


parents_post_view = ParentsPostAPI.as_view('add_parents')
parents_bp.add_url_rule('/users/<child_user_id>/parents/<parent_user_id>',
                        view_func=parents_post_view, methods=['POST'])

parents_delete_view = ParentsDeleteAPI.as_view('delete_parents')
parents_bp.add_url_rule('/users/<child_user_id>/parents/<parent_user_id>',
                        view_func=parents_delete_view, methods=['DELETE'])

parents_post_alt_view = ParentsPostAltAPI.as_view('add_parents_alt')
parents_bp.add_url_rule('/users/<child_user_id>/parents',
                        view_func=parents_post_alt_view, methods=['POST'])

from flask import Blueprint, request, jsonify
from flask.views import MethodView
from pydantic import ValidationError
from ..services.mfa_service import setup_mfa, enable_mfa, disable_mfa, verify_mfa, get_mfa_status
from ..models import MFACodeRequest, MFAStatusResponse, MFASetupResponse, ErrorResponse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity, create_access_token
from datetime import timedelta

mfa_bp = Blueprint('mfa', __name__)


class SetupAPI(MethodView):
    @jwt_required()
    def post(self):
        """
        Set up MFA for the authenticated user.
        """
        user_id = get_jwt_identity()

        result, status_code = setup_mfa(user_id)

        if status_code == 200:
            response = MFASetupResponse(
                status=result["status"],
                secret=result.get("secret"),
                backup_codes=result.get("backup_codes"),
                provisioning_uri=result.get("provisioning_uri")
            )
            return jsonify(response.model_dump()), status_code
        else:
            error_response = ErrorResponse(
                error=result.get("message", "Unknown error"))
            return jsonify(error_response.model_dump()), status_code


class EnableAPI(MethodView):
    @jwt_required()
    def post(self):
        """
        Enable MFA for the authenticated user after verifying a code.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])

            data = MFACodeRequest.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400

        user_id = get_jwt_identity()
        result, status_code = enable_mfa(user_id, data.code)

        if status_code == 200:
            return jsonify(result), status_code
        else:
            error_response = ErrorResponse(
                error=result.get("message", "Unknown error"))
            return jsonify(error_response.model_dump()), status_code


class DisableAPI(MethodView):
    @jwt_required()
    def post(self):
        """
        Disable MFA for the authenticated user after verifying a code.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])

            data = MFACodeRequest.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400

        user_id = get_jwt_identity()
        result, status_code = disable_mfa(user_id, data.code)

        if status_code == 200:
            return jsonify(result), status_code
        else:
            error_response = ErrorResponse(
                error=result.get("message", "Unknown error"))
            return jsonify(error_response.model_dump()), status_code


class VerifyAPI(MethodView):
    @jwt_required()
    def post(self):
        """
        Verify an MFA code and return a full access token.
        """
        try:
            json_data = request.get_json()
            if not json_data:
                raise ValidationError([{
                    "loc": ["body"],
                    "msg": "No JSON data provided",
                    "type": "value_error.no_json"
                }])

            data = MFACodeRequest.model_validate(json_data)
        except ValidationError as ve:
            error_response = ErrorResponse(error=str(ve))
            return jsonify(error_response.model_dump()), 400

        user_id = get_jwt_identity()
        jwt_data = get_jwt()

        if not jwt_data.get("temp_auth"):
            error_response = ErrorResponse(
                error="Invalid token for MFA verification")
            return jsonify(error_response.model_dump()), 400

        result, status_code = verify_mfa(user_id, data.code)

        if status_code == 200:
            token_payload = {k: v for k, v in jwt_data.items() if k not in [
                'temp_auth', 'requires_mfa', 'exp', 'iat', 'jti']}

            expires = timedelta(days=1)
            access_token = create_access_token(
                identity=user_id,
                additional_claims=token_payload,
                expires_delta=expires
            )

            return jsonify({
                "status": "Success",
                "token": access_token,
                "user": {
                    "user_id": token_payload.get("user_id"),
                    "user_type": token_payload.get("user_type"),
                    "name": token_payload.get("name"),
                    "medical_insurance_id": token_payload.get("medical_insurance_id"),
                    "requires_mfa": False
                }
            }), 200
        else:
            error_response = ErrorResponse(error=result.get(
                "message", "MFA verification failed"))
            return jsonify(error_response.model_dump()), status_code


class StatusAPI(MethodView):
    @jwt_required()
    def get(self):
        """
        Get the MFA status for the authenticated user.
        """
        user_id = get_jwt_identity()

        result, status_code = get_mfa_status(user_id)

        if status_code == 200:
            response = MFAStatusResponse(
                status=result["status"],
                mfa_configured=result.get("mfa_configured", False),
                mfa_enabled=result.get("mfa_enabled", False),
                configured_at=result.get("configured_at"),
                last_modified=result.get("last_modified")
            )
            return jsonify(response.model_dump()), status_code
        else:
            error_response = ErrorResponse(
                error=result.get("message", "Unknown error"))
            return jsonify(error_response.model_dump()), status_code


setup_mfa_view = SetupAPI.as_view('setup_mfa')
mfa_bp.add_url_rule('/setup', view_func=setup_mfa_view, methods=['POST'])

enable_mfa_view = EnableAPI.as_view('enable_mfa')
mfa_bp.add_url_rule('/enable', view_func=enable_mfa_view, methods=['POST'])

disable_mfa_view = DisableAPI.as_view('disable_mfa')
mfa_bp.add_url_rule('/disable', view_func=disable_mfa_view, methods=['POST'])

verify_mfa_view = VerifyAPI.as_view('verify_mfa')
mfa_bp.add_url_rule('/verify', view_func=verify_mfa_view, methods=['POST'])

status_mfa_view = StatusAPI.as_view('status_mfa')
mfa_bp.add_url_rule('/status', view_func=status_mfa_view, methods=['GET'])

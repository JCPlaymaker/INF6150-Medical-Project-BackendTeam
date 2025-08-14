from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("user_type") == "ADMIN":
                return fn(*args, **kwargs)
            else:
                return jsonify({"error": "Admin privileges required"}), 403
        return decorator
    return wrapper


def doctor_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("user_type") == "DOCTOR":
                return fn(*args, **kwargs)
            else:
                return jsonify({"error": "Doctor privileges required"}), 403
        return decorator
    return wrapper


def patient_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("user_type") == "PATIENT":
                return fn(*args, **kwargs)
            else:
                return jsonify({"error": "Patient privileges required"}), 403
        return decorator
    return wrapper


def healthcare_professional_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("user_type") == "HEALTHCARE PROFESSIONAL":
                return fn(*args, **kwargs)
            else:
                return jsonify({"error": "Healthcare professional privileges required"}), 403
        return decorator
    return wrapper


def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("user_type") == role:
                return fn(*args, **kwargs)
            else:
                return jsonify({"error": f"{role} privileges required"}), 403
        return decorator
    return wrapper


def roles_required(allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("user_type") in allowed_roles:
                return fn(*args, **kwargs)
            else:
                return jsonify({"error": "Insufficient privileges"}), 403
        return decorator
    return wrapper


def self_or_admin_access(param_name='medical_insurance_id'):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("user_type") == "ADMIN":
                return fn(*args, **kwargs)
            if claims.get("user_type") == "PATIENT":
                if claims.get("medical_insurance_id") == kwargs.get(param_name):
                    return fn(*args, **kwargs)
            return jsonify({"error": "Access denied"}), 403
        return decorator
    return wrapper


def self_doctor_or_admin_access(param_name='medical_insurance_id'):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("user_type") == "ADMIN":
                return fn(*args, **kwargs)
            if claims.get("user_type") == "DOCTOR":
                return fn(*args, **kwargs)
            if claims.get("user_type") == "PATIENT":
                if claims.get("medical_insurance_id") == kwargs.get(param_name):
                    return fn(*args, **kwargs)
            return jsonify({"error": "Access denied"}), 403
        return decorator
    return wrapper


def self_user_doctor_or_admin_access(param_name='user_id'):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("user_type") == "ADMIN":
                return fn(*args, **kwargs)
            if claims.get("user_type") == "DOCTOR":
                return fn(*args, **kwargs)
            if claims.get("user_type") == "PATIENT":
                if claims.get("user_id") == kwargs.get(param_name):
                    return fn(*args, **kwargs)
            return jsonify({"error": "Access denied"}), 403
        return decorator
    return wrapper

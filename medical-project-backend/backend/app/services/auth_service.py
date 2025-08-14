from typing import Dict, Any
from psycopg2.errors import ForeignKeyViolation
from ..models import Login
from flask import current_app
from ..db import Database
from flask_jwt_extended import create_access_token
import datetime
from ..services.token_service import add_token_to_blacklist
from ..services.mfa_service import check_mfa_enabled


def login(data: Login) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    bcrypt = current_app.config['BCRYPT']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_user_query = """
                    SELECT user_id, login, user_type, password_hash,
                        first_name, last_name, medical_insurance_id
                    FROM users
                    WHERE email = %s AND hidden IS NOT TRUE
                    ORDER BY modified_at DESC
                    LIMIT 1;
                """
                cur.execute(select_user_query, (
                    data.email,
                ))
                user_row = cur.fetchone()

                if not user_row:
                    return {"status": "Wrong credentials"}, 401

                user_id, login, user_type, password_hash, first_name, last_name, medical_insurance_id = user_row

                if bcrypt.check_password_hash(password_hash, data.password):
                    mfa_enabled = check_mfa_enabled(user_id)

                    token_payload = {
                        'user_id': user_id,
                        'login': login,
                        'user_type': user_type,
                        'name': f"{first_name} {last_name}",
                        'medical_insurance_id': medical_insurance_id
                    }

                    expires = datetime.timedelta(days=1)

                    if mfa_enabled:
                        temp_expires = datetime.timedelta(minutes=5)
                        access_token = create_access_token(
                            identity=user_id,
                            additional_claims={
                                **token_payload, 'temp_auth': True,
                                'requires_mfa': True},
                            expires_delta=temp_expires
                        )

                        return {
                            "status": "MFA Required",
                            "temp_token": access_token,
                            "user": {
                                "user_id": user_id,
                                "user_type": user_type,
                                "name": f"{first_name} {last_name}",
                                "medical_insurance_id": medical_insurance_id,
                                "requires_mfa": True
                            }
                        }, 200
                    else:
                        access_token = create_access_token(
                            identity=user_id,
                            additional_claims=token_payload,
                            expires_delta=expires
                        )

                        return {
                            "status": "Success",
                            "token": access_token,
                            "user": {
                                "user_id": user_id,
                                "user_type": user_type,
                                "name": f"{first_name} {last_name}",
                                "medical_insurance_id": medical_insurance_id,
                                "requires_mfa": False
                            }
                        }, 200
                else:
                    return {"status": "Wrong credentials"}, 401

    except ForeignKeyViolation:
        raise ForeignKeyViolation("Invalid foreign key reference.")
    except Exception as e:
        raise e


def logout(token_jti: str, user_id: str, expires_at: datetime.datetime) -> tuple[Dict[str, Any], int]:
    try:
        add_token_to_blacklist(token_jti, 'access', user_id, expires_at)

        return {"status": "Successfully logged out"}, 200
    except Exception as e:
        current_app.logger.error(f"Error during logout: {str(e)}")
        return {"status": "Error during logout", "error": str(e)}, 500

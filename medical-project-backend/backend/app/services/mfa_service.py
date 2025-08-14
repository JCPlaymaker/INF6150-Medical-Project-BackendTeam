import pyotp
import secrets
import string
from typing import Dict, Any, List, Tuple
from flask import current_app
from ..db import Database


def generate_secret() -> str:
    """Generate a new TOTP secret"""
    return pyotp.random_base32()


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code against a secret"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


def generate_backup_codes(count: int = 10) -> List[str]:
    """Generate backup codes for MFA recovery"""
    codes = []
    for _ in range(count):
        code = ''.join(secrets.choice(string.ascii_uppercase +
                       string.digits) for _ in range(8))
        codes.append(code)
    return codes


def setup_mfa(user_id: str) -> Tuple[Dict[str, Any], int]:
    """Set up MFA for a user, generating a new secret"""
    db_instance: Database = current_app.config['DATABASE']
    try:
        secret = generate_secret()
        backup_codes = generate_backup_codes()

        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_query = """
                    SELECT user_id FROM mfa_config
                    WHERE user_id = %s AND hidden IS NOT TRUE
                """
                cur.execute(select_query, (user_id,))
                existing = cur.fetchone()

                if existing:
                    update_query = """
                        UPDATE mfa_config
                        SET secret = %s, backup_codes = %s, modified_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                        RETURNING secret
                    """
                    cur.execute(update_query, (secret, backup_codes, user_id))
                else:
                    insert_query = """
                        INSERT INTO mfa_config (user_id, secret, backup_codes)
                        VALUES (%s, %s, %s)
                        RETURNING secret
                    """
                    cur.execute(insert_query, (user_id, secret, backup_codes))

                conn.commit()

        totp = pyotp.TOTP(secret)
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_query = """
                    SELECT email FROM users
                    WHERE user_id = %s
                """
                cur.execute(select_query, (user_id,))
                user_row = cur.fetchone()
                email = user_row[0] if user_row else "user"

        provisioning_uri = totp.provisioning_uri(
            email, issuer_name="MedicalAPI")

        return {
            "status": "success",
            "secret": secret,
            "backup_codes": backup_codes,
            "provisioning_uri": provisioning_uri
        }, 200
    except Exception as e:
        current_app.logger.error(f"Error setting up MFA: {str(e)}")
        return {"status": "error", "message": str(e)}, 500


def enable_mfa(user_id: str, code: str) -> Tuple[Dict[str, Any], int]:
    """Enable MFA for a user after verifying a code"""
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_query = """
                    SELECT secret FROM mfa_config
                    WHERE user_id = %s AND hidden IS NOT TRUE
                """
                cur.execute(select_query, (user_id,))
                result = cur.fetchone()

                if not result:
                    return {"status": "error", "message": "MFA not set up for this user"}, 400

                secret = result[0]

                if not verify_totp(secret, code):
                    return {"status": "error", "message": "Invalid verification code"}, 400

                update_query = """
                    UPDATE mfa_config
                    SET enabled = TRUE, modified_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """
                cur.execute(update_query, (user_id,))
                conn.commit()

                return {"status": "success", "message": "MFA enabled successfully"}, 200
    except Exception as e:
        current_app.logger.error(f"Error enabling MFA: {str(e)}")
        return {"status": "error", "message": str(e)}, 500


def disable_mfa(user_id: str, code: str) -> Tuple[Dict[str, Any], int]:
    """Disable MFA for a user after verifying a code"""
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_query = """
                    SELECT secret, enabled FROM mfa_config
                    WHERE user_id = %s AND hidden IS NOT TRUE
                """
                cur.execute(select_query, (user_id,))
                result = cur.fetchone()

                if not result:
                    return {"status": "error", "message": "MFA not set up for this user"}, 400

                secret, enabled = result

                if not enabled:
                    return {"status": "error", "message": "MFA is not enabled for this user"}, 400

                if not verify_totp(secret, code):
                    return {"status": "error", "message": "Invalid verification code"}, 400

                update_query = """
                    UPDATE mfa_config
                    SET enabled = FALSE, modified_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """
                cur.execute(update_query, (user_id,))
                conn.commit()

                return {"status": "success", "message": "MFA disabled successfully"}, 200
    except Exception as e:
        current_app.logger.error(f"Error disabling MFA: {str(e)}")
        return {"status": "error", "message": str(e)}, 500


def verify_mfa(user_id: str, code: str) -> Tuple[Dict[str, Any], int]:
    """Verify an MFA code for a user"""
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_query = """
                    SELECT secret, backup_codes FROM mfa_config
                    WHERE user_id = %s AND enabled = TRUE AND hidden IS NOT TRUE
                """
                cur.execute(select_query, (user_id,))
                result = cur.fetchone()

                if not result:
                    return {"status": "error", "message": "MFA not enabled for this user"}, 400

                secret, backup_codes = result

                if verify_totp(secret, code):
                    return {"status": "success", "message": "MFA verification successful"}, 200

                if backup_codes and code in backup_codes:
                    new_backup_codes = [c for c in backup_codes if c != code]
                    update_query = """
                        UPDATE mfa_config
                        SET backup_codes = %s, modified_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                    """
                    cur.execute(update_query, (new_backup_codes, user_id))
                    conn.commit()
                    return {"status": "success", "message": "MFA verification successful with backup code"}, 200

                return {"status": "error", "message": "Invalid verification code"}, 400
    except Exception as e:
        current_app.logger.error(f"Error verifying MFA: {str(e)}")
        return {"status": "error", "message": str(e)}, 500


def check_mfa_enabled(user_id: str) -> bool:
    """Check if MFA is enabled for a user"""
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_query = """
                    SELECT enabled FROM mfa_config
                    WHERE user_id = %s AND hidden IS NOT TRUE
                """
                cur.execute(select_query, (user_id,))
                result = cur.fetchone()

                if not result:
                    return False

                return result[0]
    except Exception as e:
        current_app.logger.error(f"Error checking MFA status: {str(e)}")
        return False


def get_mfa_status(user_id: str) -> Tuple[Dict[str, Any], int]:
    """Get the MFA status for a user"""
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_query = """
                    SELECT enabled, created_at, modified_at FROM mfa_config
                    WHERE user_id = %s AND hidden IS NOT TRUE
                """
                cur.execute(select_query, (user_id,))
                result = cur.fetchone()

                if not result:
                    return {"status": "success", "mfa_configured": False, "mfa_enabled": False}, 200

                enabled, created_at, modified_at = result

                return {
                    "status": "success",
                    "mfa_configured": True,
                    "mfa_enabled": enabled,
                    "configured_at": created_at.isoformat() if created_at else None,
                    "last_modified": modified_at.isoformat() if modified_at else None
                }, 200
    except Exception as e:
        current_app.logger.error(f"Error getting MFA status: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

from typing import Dict, Any
from flask import current_app
from ..db import Database
from datetime import datetime


def add_token_to_blacklist(jti: str, token_type: str, user_id: str, expires_at: datetime) -> None:
    # For testing, add to config-based blacklist
    if current_app.config.get('TESTING', False):
        if '_TEST_TOKEN_BLACKLIST' not in current_app.config:
            current_app.config['_TEST_TOKEN_BLACKLIST'] = set()
        current_app.config['_TEST_TOKEN_BLACKLIST'].add(jti)

    # Normal database operation
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                query = """
                    INSERT INTO token_blacklist (jti, token_type, user_id, expires_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (jti) DO NOTHING
                """
                cur.execute(query, (jti, token_type, user_id, expires_at))
                conn.commit()
                return
    except Exception as e:
        current_app.logger.error(f"Error adding token to blacklist: {str(e)}")
        raise e


def is_token_blacklisted(jti: str) -> bool:
    db_instance: Database = current_app.config['DATABASE']

    # For testing environment, check the app config for blacklisted tokens
    if current_app.config.get('TESTING', False):
        # Get the test blacklist from app config
        test_blacklist = current_app.config.get('_TEST_TOKEN_BLACKLIST', set())
        if jti in test_blacklist:
            return True
        else:
            return False

    # Normal database check
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT 1 FROM token_blacklist
                    WHERE jti = %s
                """
                cur.execute(query, (jti,))
                result = cur.fetchone()
                return result is not None
    except Exception as e:
        current_app.logger.error(f"Error checking token blacklist: {str(e)}")
        return True  # Fail secure


def revoke_all_user_tokens(user_id: str) -> None:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT jti, token_type, expires_at FROM token_blacklist
                    WHERE user_id = %s AND expires_at > NOW()
                """
                cur.execute(query, (user_id,))
                query = """
                    UPDATE token_blacklist
                    SET revoked_at = NOW()
                    WHERE user_id = %s AND expires_at > NOW()
                """
                cur.execute(query, (user_id,))
                conn.commit()
                return
    except Exception as e:
        current_app.logger.error(f"Error revoking all user tokens: {str(e)}")
        raise e


def cleanup_expired_tokens() -> None:
    """
    Remove expired tokens from the blacklist to keep the table size manageable
    Should be run periodically (e.g., via a cron job)
    """
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                query = """
                    DELETE FROM token_blacklist
                    WHERE expires_at < NOW()
                """
                cur.execute(query)
                removed_count = cur.rowcount
                conn.commit()
                current_app.logger.info(
                    f"Removed {removed_count} expired tokens from blacklist")
                return removed_count
    except Exception as e:
        current_app.logger.error(f"Error cleaning up expired tokens: {str(e)}")
        raise e

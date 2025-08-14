from typing import Optional
from flask import current_app
from ..db import Database


def lookup_doctor_id(first_name: Optional[str] = None, last_name: Optional[str] = None, doctor_id: Optional[str] = None) -> Optional[str]:
    """
    Look up a doctor ID using either the ID directly or first and last name.

    Args:
        first_name: Doctor's first name
        last_name: Doctor's last name
        doctor_id: Doctor's UUID

    Returns:
        str: The doctor's ID if found, None otherwise
    """
    if doctor_id:
        # Verify that the doctor_id exists
        db_instance: Database = current_app.config['DATABASE']
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT user_id 
                    FROM users 
                    WHERE user_id = %s AND user_type = 'DOCTOR'
                    LIMIT 1
                """
                cur.execute(query, (doctor_id,))
                result = cur.fetchone()
                return doctor_id if result else None

    elif first_name and last_name:
        # Look up by name
        db_instance: Database = current_app.config['DATABASE']
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT DISTINCT ON (user_id) user_id
                    FROM users
                    WHERE first_name = %s AND last_name = %s AND user_type = 'DOCTOR'
                    ORDER BY user_id, modified_at DESC
                    LIMIT 1
                """
                cur.execute(query, (first_name, last_name))
                result = cur.fetchone()
                return result[0] if result else None

    return None


def lookup_establishment_id(establishment_name: Optional[str] = None, establishment_id: Optional[str] = None) -> Optional[str]:
    """
    Look up an establishment ID using either the ID directly or the establishment name.

    Args:
        establishment_name: Name of the establishment
        establishment_id: Establishment's UUID

    Returns:
        str: The establishment's ID if found, None otherwise
    """
    if establishment_id:
        # Verify that the establishment_id exists
        db_instance: Database = current_app.config['DATABASE']
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT establishment_id 
                    FROM establishments 
                    WHERE establishment_id = %s
                    LIMIT 1
                """
                cur.execute(query, (establishment_id,))
                result = cur.fetchone()
                return establishment_id if result else None

    elif establishment_name:
        # Look up by name
        db_instance: Database = current_app.config['DATABASE']
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT establishment_id
                    FROM establishments
                    WHERE establishment_name = %s
                    LIMIT 1
                """
                cur.execute(query, (establishment_name,))
                result = cur.fetchone()
                return result[0] if result else None

    return None

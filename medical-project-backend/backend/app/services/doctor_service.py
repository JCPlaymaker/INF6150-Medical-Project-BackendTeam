from typing import Dict, Any, List
from flask import current_app
from ..db import Database
from ..models import DoctorListResponse
from psycopg2.errors import ForeignKeyViolation


def get_all_doctors() -> tuple[Dict[str, Any], int]:
    """
    Retrieve all users with DOCTOR user type.

    Returns:
        tuple[Dict[str, Any], int]: A tuple containing response data and status code
    """
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                doctors_query = """
                    SELECT DISTINCT ON (user_id)
                        user_id,
                        first_name,
                        last_name,
                        email,
                        phone_number,
                        modified_at
                    FROM users
                    WHERE user_type = 'DOCTOR' and hidden IS NOT TRUE
                    ORDER BY user_id, modified_at DESC;
                """
                cur.execute(doctors_query)
                doctor_rows = cur.fetchall()

                doctors = []
                for doctor in doctor_rows:
                    doctors.append({
                        "user_id": doctor[0],
                        "first_name": doctor[1],
                        "last_name": doctor[2],
                        "email": doctor[3],
                        "phone_number": doctor[4]
                    })

                doctors_response = [DoctorListResponse(
                    **doctor).model_dump() for doctor in doctors]

                return {"status": "success", "data": doctors_response}, 200

    except Exception as e:
        return {"status": "error", "message": repr(e)}, 500

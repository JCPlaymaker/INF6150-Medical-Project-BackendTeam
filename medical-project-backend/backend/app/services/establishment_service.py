from typing import Dict, Any, List
from flask import current_app
from ..db import Database
from ..models import EstablishmentListResponse
from psycopg2.errors import ForeignKeyViolation


def get_all_establishments() -> tuple[Dict[str, Any], int]:
    """
    Retrieve all medical establishments.

    Returns:
        tuple[Dict[str, Any], int]: A tuple containing response data and status code
    """
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                # Query to get all establishments
                establishments_query = """
                    SELECT
                        establishment_id,
                        establishment_name,
                        created_at
                    FROM establishments
                    WHERE hidden IS NOT TRUE
                    ORDER BY establishment_name;
                """
                cur.execute(establishments_query)
                establishment_rows = cur.fetchall()

                establishments = []
                for establishment in establishment_rows:
                    establishments.append({
                        "establishment_id": establishment[0],
                        "establishment_name": establishment[1],
                        "created_at": establishment[2]
                    })

                establishments_response = [EstablishmentListResponse(
                    **establishment).model_dump() for establishment in establishments]

                return {"status": "success", "data": establishments_response}, 200

    except Exception as e:
        return {"status": "error", "message": repr(e)}, 500


def hide_establishment(establishment_id: str) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                hide_user_query = """
                    UPDATE establishments SET hidden = TRUE WHERE establishment_id = %s
                """
                cur.execute(hide_user_query, (establishment_id, ))
                conn.commit()

                return {"status": "success"}, 200

    except ForeignKeyViolation as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": str(e)}, 500

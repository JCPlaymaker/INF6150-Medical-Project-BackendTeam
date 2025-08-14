from typing import Dict, Any
from psycopg2.errors import ForeignKeyViolation
from ..models import CoordinateCreate, HistoryCreate, CoordinateUpdate, CoordinateUpdateResponse, CoordinateCreateResponse, ParentCreate
from flask import current_app
from ..db import Database


def add_parents(child_user_id: str, parent_user_id: str) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                insert_parents_query = """
                    INSERT INTO parents (child_id, parent_id)
                    VALUES (%s, %s)
                """
                cur.execute(insert_parents_query, (
                    child_user_id,
                    parent_user_id
                ))

                conn.commit()

                return {"status": "success"}, 201

    except ForeignKeyViolation:
        return {"status": "error", "error": "Invalid foreign key reference."}, 400
    except Exception as e:
        return {"status": "error", "error": str(e)}, 500


def add_parents_alt(child_user_id: str, data: ParentCreate) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                check_existence_query = """
                    SELECT EXISTS(SELECT 1 FROM users WHERE user_id=%s)
                """
                cur.execute(check_existence_query, (
                    child_user_id,
                ))
                exist = cur.fetchone()[0]
                if not exist:
                    return {"status": "error", "error": "Invalid foreign key reference."}, 400

                insert_user_query = """
                    INSERT INTO users (first_name, last_name, phone_number, email, gender)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING user_id;
                """
                cur.execute(insert_user_query, (
                    data.first_name,
                    data.last_name,
                    data.phone_number,
                    data.email,
                    data.gender
                ))
                user_id = cur.fetchone()[0]

                insert_parents_query = """
                    INSERT INTO parents (child_id, parent_id)
                    VALUES (%s, %s)
                """
                cur.execute(insert_parents_query, (
                    child_user_id,
                    user_id,
                ))

                conn.commit()

                return {"status": "success", "user_id": user_id}, 201

    except ForeignKeyViolation:
        return {"status": "error", "error": "Invalid foreign key reference."}, 400
    except Exception as e:
        return {"status": "error", "error": str(e)}, 500


def hide_parents(child_user_id: str, parent_user_id: str) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                hide_coordinate_query = """
                    UPDATE parents SET hidden = TRUE
                    WHERE child_id = %s AND parent_id = %s
                """
                cur.execute(hide_coordinate_query,
                            (child_user_id, parent_user_id))

                conn.commit()

                return {"status": "success"}, 200

    except ForeignKeyViolation as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": str(e)}, 500

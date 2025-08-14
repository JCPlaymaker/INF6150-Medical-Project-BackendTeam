from typing import Dict, Any
from psycopg2.errors import ForeignKeyViolation
from ..models import UserCreate, UserUpdate, UserResponse, UserUpdateResponse, UserResponse, UserCreateResponse, CredentialsUpdate
from flask import current_app
from ..db import Database
import bcrypt


def add_user(data: UserCreate) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                password_bytes = (data.password).encode('utf-8')
                salt = bcrypt.gensalt()
                pwhash = bcrypt.hashpw(password_bytes, salt)
                password_hash = pwhash.decode('utf8')
                insert_user_query = """
                    INSERT INTO users (login, password_hash, user_type, first_name, last_name, phone_number, email)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING user_id;
                """
                cur.execute(insert_user_query, (
                    data.login,
                    password_hash,
                    data.user_type,
                    data.first_name,
                    data.last_name,
                    data.phone_number,
                    data.email,
                ))
                user_id = cur.fetchone()[0]
                conn.commit()

                user_response = UserCreateResponse(
                    user_id=user_id,
                )

                return {"status": "success", "data": user_response}, 201

    except ForeignKeyViolation:
        raise ForeignKeyViolation("Invalid foreign key reference.")
    except Exception as e:
        raise e


def update_user(user_id: str, data: UserUpdate) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_created_at_query = """
                    SELECT user_id, login, password_hash, user_type, first_name, last_name, phone_number, email, created_at FROM users
                    WHERE user_id = %s
                """
                cur.execute(select_created_at_query, (
                    user_id,
                ))
                user_row = cur.fetchone()

                if not user_row:
                    return {"status": "error", "message": "User not found."}, 404

                user_data = {
                    "user_id": user_row[0],
                    "login": user_row[1],
                    "password_hash": user_row[2],
                    "user_type": user_row[3],
                    "first_name": user_row[4],
                    "last_name": user_row[5],
                    "phone_number": user_row[6],
                    "email": user_row[7],
                    "created_at": user_row[8],
                }

                if data.login != "":
                    user_data["login"] = data.login

                if data.first_name != "":
                    user_data["first_name"] = data.first_name

                if data.last_name != "":
                    user_data["last_name"] = data.last_name

                if data.email != "":
                    user_data["email"] = data.email

                if data.phone_number != "":
                    user_data["phone_number"] = data.phone_number

                insert_patient_query = """
                    INSERT INTO users (user_id, login, password_hash, user_type, first_name, last_name, email, phone_number, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(insert_patient_query, (
                    user_data["user_id"],
                    user_data["login"],
                    user_data["password_hash"],
                    user_data["user_type"],
                    user_data["first_name"],
                    user_data["last_name"],
                    user_data["email"],
                    user_data["phone_number"],
                    user_data["created_at"],
                ))

                conn.commit()

        user_response = UserUpdateResponse(
            user_id=user_id,
            login=user_data["login"],
            user_type=user_data["user_type"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            phone_number=user_data["phone_number"],
            created_at=user_data["created_at"],
        )
        return {"status": "success", "data": user_response}, 201

    except ForeignKeyViolation:
        raise ForeignKeyViolation("Invalid foreign key reference.")
    except Exception as e:
        raise e


def update_user_credentials(user_id: str, data: CredentialsUpdate) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_created_at_query = """
                    SELECT user_id, login, password_hash, user_type, first_name, last_name, phone_number, email, created_at, medical_insurance_id FROM users
                    WHERE user_id = %s
                """
                cur.execute(select_created_at_query, (
                    user_id,
                ))
                user_row = cur.fetchone()

                if not user_row:
                    return {"status": "error", "message": "User not found."}, 404

                user_data = {
                    "user_id": user_row[0],
                    "login": user_row[1],
                    "password_hash": user_row[2],
                    "user_type": user_row[3],
                    "first_name": user_row[4],
                    "last_name": user_row[5],
                    "phone_number": user_row[6],
                    "email": user_row[7],
                    "created_at": user_row[8],
                    "medical_insurance_id": user_row[9],
                }

                if data.login != "":
                    user_data["login"] = data.login

                if data.password != "":
                    password_bytes = (data.password).encode('utf-8')
                    salt = bcrypt.gensalt()
                    pwhash = bcrypt.hashpw(password_bytes, salt)
                    password_hash = pwhash.decode('utf8')
                    user_data["password_hash"] = password_hash

                insert_patient_query = """
                    INSERT INTO users (user_id, login, password_hash, user_type, first_name, last_name, email, phone_number, created_at, medical_insurance_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(insert_patient_query, (
                    user_data["user_id"],
                    user_data["login"],
                    user_data["password_hash"],
                    user_data["user_type"],
                    user_data["first_name"],
                    user_data["last_name"],
                    user_data["email"],
                    user_data["phone_number"],
                    user_data["created_at"],
                    user_data["medical_insurance_id"],
                ))

                conn.commit()

        return {"status": "success"}, 201

    except ForeignKeyViolation as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": str(e)}, 500


def get_user(user_id: str) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                patient_query = """
                    SELECT
                        login,
                        user_type,
                        first_name,
                        last_name,
                        phone_number,
                        email,
                        modified_at,
                        created_at
                    FROM users
                    WHERE user_id = %s AND hidden IS NOT TRUE
                    ORDER BY modified_at DESC
                    LIMIT 1;
                """
                cur.execute(patient_query, (user_id,))
                user_row = cur.fetchone()

                if not user_row:
                    return {"status": "error", "message": "User not found."}, 404

                user_data = {
                    "login": user_row[0],
                    "user_type": user_row[1],
                    "first_name": user_row[2],
                    "last_name": user_row[3],
                    "phone_number": user_row[4],
                    "email": user_row[5],
                    "modified_at": user_row[6],
                    "created_at": user_row[7]
                }

                user_response = UserResponse(
                    user_id=user_id,
                    login=user_data["login"],
                    user_type=user_data["user_type"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    email=user_data["email"],
                    phone_number=user_data["phone_number"],
                    created_at=user_data["created_at"],
                    modified_at=user_data["modified_at"],
                )

                return {"status": "success", "data": user_response}, 200

    except ForeignKeyViolation:
        return {"status": "error", "message": "Invalid foreign key reference."}, 400
    except Exception as e:
        return {"status": "error", "message": repr(e)}, 500


def hide_user(user_id: str) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                hide_user_query = """
                    UPDATE users SET hidden = TRUE WHERE user_id = %s
                """
                cur.execute(hide_user_query, (user_id, ))
                conn.commit()

                return {"status": "success"}, 200

    except ForeignKeyViolation as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": str(e)}, 500

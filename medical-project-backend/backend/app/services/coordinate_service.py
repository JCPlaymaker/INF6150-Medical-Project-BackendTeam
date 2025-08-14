from typing import Dict, Any
from psycopg2.errors import ForeignKeyViolation
from ..models import CoordinateCreate, HistoryCreate, CoordinateUpdate, CoordinateUpdateResponse, CoordinateCreateResponse, PatientUpdateResponse, EmailPhoneUpdate
from flask import current_app
from ..db import Database


def add_coordinates(user_id: str, data: CoordinateCreate) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                insert_history_query = """
                    INSERT INTO coordinates (user_id, street_address,
                                                 postal_code, city,
                                                 country)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING coordinate_id;
                """
                cur.execute(insert_history_query, (
                    user_id,
                    data.street_address,
                    data.postal_code,
                    data.city,
                    data.country
                ))
                coordinate_id = cur.fetchone()[0]

                conn.commit()

                coordinate_response = CoordinateCreateResponse(
                    coordinate_id=coordinate_id,
                )

                return {"status": "success", "message": coordinate_response}, 201

    except ForeignKeyViolation:
        return {"status": "error", "message": "Invalid foreign key reference."}, 400
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


def update_coordinates(coordinate_id: str, data: CoordinateUpdate) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_previous_coordinate_query = """
                    SELECT user_id, street_address, apartment,
                        postal_code, city, country, created_at
                    FROM coordinates
                    WHERE coordinate_id = %s
                """
                cur.execute(select_previous_coordinate_query, (
                    coordinate_id,
                ))
                coordinate_row = cur.fetchone()

                if not coordinate_row:
                    return {"status": "error", "message": "Coordinate not found."}, 404

                coordinate_data = {
                    "user_id": coordinate_row[0],
                    "street_address": coordinate_row[1],
                    "apartment": coordinate_row[2],
                    "postal_code": coordinate_row[3],
                    "city": coordinate_row[4],
                    "country": coordinate_row[5],
                    "created_at": coordinate_row[6]
                }

                if data.street_address != "":
                    coordinate_data["street_address"] = data.street_address

                if data.apartment != "":
                    coordinate_data["apartment"] = data.apartment

                if data.postal_code != "":
                    coordinate_data["postal_code"] = data.postal_code

                if data.city != "":
                    coordinate_data["city"] = data.city

                if data.country != "":
                    coordinate_data["country"] = data.country

                insert_history_query = """
                    INSERT INTO coordinates (coordinate_id, user_id,
                                                 street_address,
                                                 apartment, postal_code,
                                                 city, country,
                                                 created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """
                cur.execute(insert_history_query, (
                    coordinate_id,
                    coordinate_data["user_id"],
                    coordinate_data["street_address"],
                    coordinate_data["apartment"],
                    coordinate_data["postal_code"],
                    coordinate_data["city"],
                    coordinate_data["country"],
                    coordinate_data["created_at"],
                ))

                conn.commit()

        coordinate_response = CoordinateUpdateResponse(
            coordinate_id=coordinate_id,
            user_id=coordinate_data["user_id"],
            street_address=coordinate_data["street_address"],
            apartment=coordinate_data["apartment"],
            postal_code=coordinate_data["postal_code"],
            city=coordinate_data["city"],
            country=coordinate_data["country"],
        )
        return {"status": "success", "data": coordinate_response}, 201

    except ForeignKeyViolation:
        raise ForeignKeyViolation("Invalid foreign key reference.")
    except Exception as e:
        raise e


def update_email_phone(user_id: str, data: EmailPhoneUpdate) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_created_at_query = """
                    SELECT user_id, login, password_hash, user_type, first_name, last_name, phone_number, email, gender, city_of_birth, date_of_birth, created_at, medical_insurance_id FROM users
                    WHERE user_id = %s
                """
                cur.execute(select_created_at_query, (
                    user_id,
                ))
                patient_row = cur.fetchone()

                if not patient_row:
                    return {"status": "error", "message": "Patient not found."}, 404

                patient_data = {
                    "user_id": patient_row[0],
                    "login": patient_row[1],
                    "password_hash": patient_row[2],
                    "user_type": patient_row[3],
                    "first_name": patient_row[4],
                    "last_name": patient_row[5],
                    "phone_number": patient_row[6],
                    "email": patient_row[7],
                    "gender": patient_row[8],
                    "city_of_birth": patient_row[9],
                    "date_of_birth": patient_row[10],
                    "created_at": patient_row[11],
                    "medical_insurance_id": patient_row[12]
                }

                if data.email != "":
                    patient_data["email"] = data.email

                if data.phone_number != "":
                    patient_data["phone_number"] = data.phone_number

                insert_patient_query = """
                    INSERT INTO users (user_id, login, password_hash, user_type, first_name, last_name,
                                       medical_insurance_id, gender, city_of_birth, email, phone_number,
                                       date_of_birth, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(insert_patient_query, (
                    user_id,
                    patient_data["login"],
                    patient_data["password_hash"],
                    patient_data["user_type"],
                    patient_data["first_name"],
                    patient_data["last_name"],
                    patient_data["medical_insurance_id"],
                    patient_data["gender"],
                    patient_data["city_of_birth"],
                    patient_data["email"],
                    patient_data["phone_number"],
                    patient_data["date_of_birth"],
                    patient_data["created_at"],
                ))

                conn.commit()

        patient_response = PatientUpdateResponse(
            user_id=user_id,
            login=patient_data["login"],
            user_type=patient_data["user_type"],
            first_name=patient_data["first_name"],
            last_name=patient_data["last_name"],
            medical_insurance_id=patient_data["medical_insurance_id"],
            gender=patient_data["gender"],
            city_of_birth=patient_data["city_of_birth"],
            email=patient_data["email"],
            phone_number=patient_data["phone_number"],
            created_at=patient_data["created_at"],
            date_of_birth=patient_data["date_of_birth"],
        )
        return {"status": "success", "data": patient_response}, 201

    except ForeignKeyViolation:
        raise ForeignKeyViolation("Invalid foreign key reference.")
    except Exception as e:
        raise e


def hide_coordinates(coordinate_id: str) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                hide_coordinate_query = """
                    UPDATE coordinates SET hidden = TRUE
                    WHERE coordinate_id = %s
                """
                cur.execute(hide_coordinate_query, (coordinate_id, ))

                conn.commit()

                return {"status": "success"}, 200

    except ForeignKeyViolation as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": str(e)}, 500

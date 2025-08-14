from typing import Dict, Any
from psycopg2.errors import ForeignKeyViolation
from ..models import PatientCreate, PatientUpdate, PatientResponse, PatientUpdateResponse, PatientCreateResponse, CoordinateResponse, MedicalHistoryResponse, MedicalVisitResponse, ParentResponse
from flask import current_app
from ..db import Database
from datetime import date, datetime
import bcrypt


def add_patient(data: PatientCreate) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                password_bytes = (data.password).encode('utf-8')
                salt = bcrypt.gensalt()
                pwhash = bcrypt.hashpw(password_bytes, salt)
                password_hash = pwhash.decode('utf8')
                insert_user_query = """
                    INSERT INTO users (login, password_hash, user_type, first_name, last_name, phone_number, email, medical_insurance_id, gender, city_of_birth, date_of_birth)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    data.medical_insurance_id,
                    data.gender,
                    data.city_of_birth,
                    data.date_of_birth
                ))
                user_id = cur.fetchone()[0]

                coordinates_ids = []
                for coordinate in data.coordinates:
                    insert_coordinates_query = """
                        INSERT INTO coordinates (user_id, street_address, apartment, postal_code, city, country)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING coordinate_id;
                    """
                    cur.execute(insert_coordinates_query, (
                        user_id,
                        coordinate.street_address,
                        coordinate.apartment,
                        coordinate.postal_code,
                        coordinate.city,
                        coordinate.country
                    ))
                    coordinate_id = cur.fetchone()[0]
                    coordinates_ids.append(coordinate_id)

                if data.parent_ids:
                    for parent_id in data.parent_ids:
                        insert_parent_query = """
                            INSERT INTO parents (parent_id, child_id)
                            VALUES (%s, %s)
                            ON CONFLICT (parent_id, child_id) DO NOTHING;
                        """
                        cur.execute(insert_parent_query, (
                            parent_id,
                            user_id
                        ))

                conn.commit()

                patient_response = PatientCreateResponse(
                    user_id=user_id,
                )

                return {"status": "success", "data": patient_response}, 201

    except ForeignKeyViolation:
        raise ForeignKeyViolation("Invalid foreign key reference.")
    except Exception as e:
        raise e


def update_patient(medical_insurance_id: str, data: PatientUpdate) -> tuple[Dict[str, Any], int]:
    from datetime import datetime
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_created_at_query = """
                    SELECT user_id, login, password_hash, user_type, first_name, last_name, phone_number, email, gender, city_of_birth, date_of_birth, created_at FROM users
                    WHERE medical_insurance_id = %s
                """
                cur.execute(select_created_at_query, (
                    medical_insurance_id,
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
                    "created_at": patient_row[11]
                }

                if data.login != "":
                    patient_data["login"] = data.login

                if data.first_name != "":
                    patient_data["first_name"] = data.first_name

                if data.last_name != "":
                    patient_data["last_name"] = data.last_name

                if data.gender != "":
                    patient_data["gender"] = data.gender

                if data.city_of_birth != "":
                    patient_data["city_of_birth"] = data.city_of_birth

                if data.date_of_birth != "":
                    patient_data["date_of_birth"] = data.date_of_birth

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
                    patient_data["user_id"],
                    patient_data["login"],
                    patient_data["password_hash"],
                    patient_data["user_type"],
                    patient_data["first_name"],
                    patient_data["last_name"],
                    medical_insurance_id,
                    patient_data["gender"],
                    patient_data["city_of_birth"],
                    patient_data["email"],
                    patient_data["phone_number"],
                    patient_data["date_of_birth"],
                    patient_data["created_at"],
                ))

                conn.commit()

        patient_response = PatientUpdateResponse(
            user_id=patient_data["user_id"],
            login=patient_data["login"],
            user_type=patient_data["user_type"],
            first_name=patient_data["first_name"],
            last_name=patient_data["last_name"],
            medical_insurance_id=medical_insurance_id,
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


def get_patient(medical_insurance_id: str) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                patient_query = """
                    SELECT
                        medical_insurance_id,
                        gender,
                        city_of_birth,
                        user_id,
                        login,
                        user_type,
                        first_name,
                        last_name,
                        phone_number,
                        email,
                        modified_at,
                        created_at,
                        date_of_birth
                    FROM users
                    WHERE medical_insurance_id = %s AND hidden IS NOT TRUE
                    ORDER BY unique_id DESC
                    LIMIT 1;
                """
                cur.execute(patient_query, (medical_insurance_id,))
                patient_row = cur.fetchone()

                if not patient_row:
                    return {"status": "error", "message": "Patient not found."}, 404

                patient_data = {
                    "medical_insurance_id": patient_row[0],
                    "gender": patient_row[1],
                    "city_of_birth": patient_row[2],
                    "user_id": patient_row[3],
                    "login": patient_row[4],
                    "user_type": patient_row[5],
                    "first_name": patient_row[6],
                    "last_name": patient_row[7],
                    "phone_number": patient_row[8],
                    "email": patient_row[9],
                    "modified_at": patient_row[10],
                    "created_at": patient_row[11],
                    "date_of_birth": patient_row[12]
                }

                coordinates_query = """
                    SELECT
                        c.coordinate_id,
                        c.street_address,
                        c.apartment,
                        c.postal_code,
                        c.city,
                        c.country,
                        c.modified_at
                    FROM (
                        SELECT
                            c.*,
                            ROW_NUMBER() OVER (PARTITION BY c.coordinate_id ORDER BY c.unique_id DESC) AS rn
                        FROM coordinates c
                        WHERE c.user_id = %s AND c.hidden IS NOT TRUE
                    ) c
                    WHERE c.rn = 1
                    ORDER BY c.coordinate_id;
                """
                cur.execute(coordinates_query,
                            (patient_row[3],))  # user_id is at index 3
                coordinates_rows = cur.fetchall()

                coordinates = [
                    {
                        "id": coord[0],
                        "street_address": coord[1],
                        "apartment": coord[2],
                        "postal_code": coord[3],
                        "city": coord[4],
                        "country": coord[5]
                    }
                    for coord in coordinates_rows
                ]
                # TODO: Join when theres multiple instance of a doctor_id
                medical_history_query = """
                    SELECT
                        mh.history_id,
                        mh.diagnostic,
                        mh.treatment,
                        d.user_id,
                        d.login,
                        d.user_type,
                        d.first_name,
                        d.last_name,
                        mh.start_date,
                        mh.end_date,
                        mh.modified_at
                    FROM (
                        SELECT
                            mh.*,
                            ROW_NUMBER() OVER (PARTITION BY mh.history_id ORDER BY mh.unique_id DESC) AS rn
                        FROM medical_history mh
                        WHERE mh.patient_id = %s AND mh.hidden IS NOT TRUE
                    ) mh
                    JOIN users d ON mh.doctor_id = d.user_id
                    WHERE mh.rn = 1;
                """
                cur.execute(medical_history_query, (medical_insurance_id,))
                medical_history_rows = cur.fetchall()

                medical_history = []
                for mh in medical_history_rows:
                    medical_history.append({
                        "id": mh[0],
                        "diagnostic": mh[1],
                        "treatment": mh[2],
                        "doctor": {
                            "id": mh[3],
                            "login": mh[4],
                            "user_type": mh[5],
                            "first_name": mh[6],
                            "last_name": mh[7]
                        },
                        "start_date": mh[8],
                        "end_date": mh[9]
                    })

                # TODO: Join when theres multiple instance of a doctor_id
                medical_visits_query = """
                    SELECT
                        mv.visit_id,
                        mv.patient_id,
                        d.user_id,
                        d.login,
                        d.user_type,
                        d.first_name,
                        d.last_name,
                        mv.visit_date,
                        mv.diagnostic_established,
                        mv.treatment,
                        mv.visit_summary,
                        mv.notes,
                        mv.created_at,
                        mv.modified_at,
                        e.establishment_id,
                        e.establishment_name,
                        e.created_at as establishment_created_at
                    FROM (
                        SELECT
                            mv.*,
                            ROW_NUMBER() OVER (PARTITION BY mv.visit_id ORDER BY mv.unique_id DESC) AS rn
                        FROM medical_visits mv
                        WHERE mv.patient_id = %s AND mv.hidden IS NOT TRUE
                    ) mv
                    LEFT JOIN users d ON mv.doctor_id = d.user_id
                    LEFT JOIN establishments e ON mv.establishment_id = e.establishment_id
                    WHERE mv.rn = 1
                    ORDER BY mv.visit_id;
                """
                cur.execute(medical_visits_query, (medical_insurance_id,))
                medical_visits_rows = cur.fetchall()

                medical_visits = [
                    {
                        "id": mv[0],
                        "patient_id": mv[1],
                        "doctor": {
                            "id": mv[2],
                            "login": mv[3],
                            "user_type": mv[4],
                            "first_name": mv[5],
                            "last_name": mv[6]
                        },
                        "visit_date": mv[7].isoformat() if mv[7] else None,
                        "diagnostic_established": mv[8],
                        "treatment": mv[9],
                        "visit_summary": mv[10],
                        "notes": mv[11],
                        "created_at": mv[12],
                        "modified_at": mv[13],
                        "establishment": {
                            "establishment_id": mv[14],
                            "establishment_name": mv[15],
                            "created_at": mv[16]
                        }
                    }
                    for mv in medical_visits_rows
                ]

                parents_query = """
                    SELECT
                        p.parent_id,
                        u.login,
                        u.user_type,
                        u.first_name,
                        u.last_name,
                        u.phone_number,
                        u.email,
                        u.created_at,
                        u.modified_at
                    FROM parents p
                    JOIN (
                        SELECT
                            *,
                            ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY modified_at DESC) AS rn
                        FROM users
                    ) u ON p.parent_id = u.user_id AND u.rn = 1
                    WHERE p.child_id = %s AND p.hidden IS NOT TRUE;
                """
                cur.execute(parents_query, (patient_data["user_id"],))
                parents_rows = cur.fetchall()

                parents = []
                for parent in parents_rows:
                    parents.append({
                        "parent": {
                            "user_id": parent[0],
                            "login": parent[1],
                            "user_type": parent[2],
                            "first_name": parent[3],
                            "last_name": parent[4],
                            "phone_number": parent[5],
                            "email": parent[6],
                            "created_at": parent[7],
                            "modified_at": parent[8]
                        }
                    })

                coordinates_response = [CoordinateResponse(
                    **coord) for coord in coordinates]
                medical_history_response = [
                    MedicalHistoryResponse(**mh) for mh in medical_history]
                medical_visits_response = [
                    MedicalVisitResponse(**mv) for mv in medical_visits]
                parents_response = [ParentResponse(
                    **parent) for parent in parents]

                patient_response = PatientResponse(
                    user_id=patient_data["user_id"],
                    login=patient_data["login"],
                    user_type=patient_data["user_type"],
                    first_name=patient_data["first_name"],
                    last_name=patient_data["last_name"],
                    medical_insurance_id=medical_insurance_id,
                    gender=patient_data["gender"],
                    city_of_birth=patient_data["city_of_birth"],
                    email=patient_data["email"],
                    phone_number=patient_data["phone_number"],
                    created_at=patient_data["created_at"],
                    modified_at=patient_data["modified_at"],
                    date_of_birth=patient_data["date_of_birth"],
                    coordinates=coordinates_response,
                    medical_history=medical_history_response,
                    medical_visits=medical_visits_response,
                    parents=parents_response
                )

                return {"status": "success", "data": patient_response}, 200

    except ForeignKeyViolation:
        return {"status": "error", "message": "Invalid foreign key reference."}, 400
    except Exception as e:
        return {"status": "error", "message": repr(e)}, 500


def get_patient_at_date(medical_insurance_id: str, date: date) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                patient_query = """
                    SELECT
                        medical_insurance_id,
                        gender,
                        city_of_birth,
                        user_id,
                        login,
                        user_type,
                        first_name,
                        last_name,
                        phone_number,
                        email,
                        modified_at,
                        created_at,
                        date_of_birth
                    FROM users
                    WHERE medical_insurance_id = %s AND hidden IS NOT TRUE AND modified_at <= %s
                    ORDER BY unique_id DESC
                    LIMIT 1;
                """
                cur.execute(patient_query, (medical_insurance_id, date))
                patient_row = cur.fetchone()

                if not patient_row:
                    return {"status": "error", "message": "Patient not found."}, 404

                patient_data = {
                    "medical_insurance_id": patient_row[0],
                    "gender": patient_row[1],
                    "city_of_birth": patient_row[2],
                    "user_id": patient_row[3],
                    "login": patient_row[4],
                    "user_type": patient_row[5],
                    "first_name": patient_row[6],
                    "last_name": patient_row[7],
                    "phone_number": patient_row[8],
                    "email": patient_row[9],
                    "modified_at": patient_row[10],
                    "created_at": patient_row[11],
                    "date_of_birth": patient_row[12]
                }

                coordinates_query = """
                    SELECT
                        c.coordinate_id,
                        c.street_address,
                        c.apartment,
                        c.postal_code,
                        c.city,
                        c.country,
                        c.modified_at
                    FROM (
                        SELECT
                            c.*,
                            ROW_NUMBER() OVER (PARTITION BY c.coordinate_id ORDER BY c.unique_id DESC) AS rn
                        FROM coordinates c
                        WHERE c.user_id = %s AND c.hidden IS NOT TRUE AND modified_at <= %s
                    ) c
                    WHERE c.rn = 1
                    ORDER BY c.coordinate_id;
                """
                cur.execute(coordinates_query,
                            (patient_row[3], date))  # user_id is at index 3
                coordinates_rows = cur.fetchall()

                coordinates = [
                    {
                        "id": coord[0],
                        "street_address": coord[1],
                        "apartment": coord[2],
                        "postal_code": coord[3],
                        "city": coord[4],
                        "country": coord[5]
                    }
                    for coord in coordinates_rows
                ]
                # TODO: Join when theres multiple instance of a doctor_id
                medical_history_query = """
                    SELECT
                        mh.history_id,
                        mh.diagnostic,
                        mh.treatment,
                        d.user_id,
                        d.login,
                        d.user_type,
                        d.first_name,
                        d.last_name,
                        mh.start_date,
                        mh.end_date,
                        mh.modified_at
                    FROM (
                        SELECT
                            mh.*,
                            ROW_NUMBER() OVER (PARTITION BY mh.history_id ORDER BY mh.unique_id DESC) AS rn
                        FROM medical_history mh
                        WHERE mh.patient_id = %s AND mh.hidden IS NOT TRUE AND modified_at = %s
                    ) mh
                    JOIN users d ON mh.doctor_id = d.user_id
                    WHERE mh.rn = 1;
                """
                cur.execute(medical_history_query,
                            (medical_insurance_id, date))
                medical_history_rows = cur.fetchall()

                medical_history = []
                for mh in medical_history_rows:
                    medical_history.append({
                        "id": mh[0],
                        "diagnostic": mh[1],
                        "treatment": mh[2],
                        "doctor": {
                            "id": mh[3],
                            "login": mh[4],
                            "user_type": mh[5],
                            "first_name": mh[6],
                            "last_name": mh[7]
                        },
                        "start_date": mh[8],
                        "end_date": mh[9]
                    })

                # TODO: Join when theres multiple instance of a doctor_id
                medical_visits_query = """
                    SELECT
                        mv.visit_id,
                        mv.patient_id,
                        d.user_id,
                        d.login,
                        d.user_type,
                        d.first_name,
                        d.last_name,
                        mv.visit_date,
                        mv.diagnostic_established,
                        mv.treatment,
                        mv.visit_summary,
                        mv.notes,
                        mv.created_at,
                        mv.modified_at,
                        e.establishment_id,
                        e.establishment_name,
                        e.created_at as establishment_created_at
                    FROM (
                        SELECT
                            mv.*,
                            ROW_NUMBER() OVER (PARTITION BY mv.visit_id ORDER BY mv.unique_id DESC) AS rn
                        FROM medical_visits mv
                        WHERE mv.patient_id = %s AND mv.hidden IS NOT TRUE AND modified_at <= %s
                    ) mv
                    LEFT JOIN users d ON mv.doctor_id = d.user_id
                    LEFT JOIN establishments e ON mv.establishment_id = e.establishment_id
                    WHERE mv.rn = 1
                    ORDER BY mv.visit_id;
                """
                cur.execute(medical_visits_query, (medical_insurance_id,))
                medical_visits_rows = cur.fetchall()

                medical_visits = [
                    {
                        "id": mv[0],
                        "patient_id": mv[1],
                        "doctor": {
                            "id": mv[2],
                            "login": mv[3],
                            "user_type": mv[4],
                            "first_name": mv[5],
                            "last_name": mv[6]
                        },
                        "visit_date": mv[7].isoformat() if mv[7] else None,
                        "diagnostic_established": mv[8],
                        "treatment": mv[9],
                        "visit_summary": mv[10],
                        "notes": mv[11],
                        "created_at": mv[12],
                        "modified_at": mv[13],
                        "establishment": {
                            "establishment_id": mv[14],
                            "establishment_name": mv[15],
                            "created_at": mv[16]
                        }
                    }
                    for mv in medical_visits_rows
                ]

                parents_query = """
                    SELECT
                        p.parent_id,
                        u.login,
                        u.user_type,
                        u.first_name,
                        u.last_name,
                        u.phone_number,
                        u.email,
                        u.created_at,
                        u.modified_at
                    FROM parents p
                    JOIN (
                        SELECT
                            *,
                            ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY modified_at DESC) AS rn
                        FROM users
                    ) u ON p.parent_id = u.user_id AND u.rn = 1
                    WHERE p.child_id = %s AND p.hidden IS NOT TRUE AND modified_at = %s;
                """
                cur.execute(parents_query, (patient_data["user_id"], date))
                parents_rows = cur.fetchall()

                parents = []
                for parent in parents_rows:
                    parents.append({
                        "parent": {
                            "user_id": parent[0],
                            "login": parent[1],
                            "user_type": parent[2],
                            "first_name": parent[3],
                            "last_name": parent[4],
                            "phone_number": parent[5],
                            "email": parent[6],
                            "created_at": parent[7],
                            "modified_at": parent[8]
                        }
                    })

                coordinates_response = [CoordinateResponse(
                    **coord) for coord in coordinates]
                medical_history_response = [
                    MedicalHistoryResponse(**mh) for mh in medical_history]
                medical_visits_response = [
                    MedicalVisitResponse(**mv) for mv in medical_visits]
                parents_response = [ParentResponse(
                    **parent) for parent in parents]

                patient_response = PatientResponse(
                    user_id=patient_data["user_id"],
                    login=patient_data["login"],
                    user_type=patient_data["user_type"],
                    first_name=patient_data["first_name"],
                    last_name=patient_data["last_name"],
                    medical_insurance_id=medical_insurance_id,
                    gender=patient_data["gender"],
                    city_of_birth=patient_data["city_of_birth"],
                    email=patient_data["email"],
                    phone_number=patient_data["phone_number"],
                    created_at=patient_data["created_at"],
                    modified_at=patient_data["modified_at"],
                    date_of_birth=patient_data["date_of_birth"],
                    coordinates=coordinates_response,
                    medical_history=medical_history_response,
                    medical_visits=medical_visits_response,
                    parents=parents_response
                )

                return {"status": "success", "data": patient_response}, 200

    except ForeignKeyViolation:
        return {"status": "error", "message": "Invalid foreign key reference."}, 400
    except Exception as e:
        return {"status": "error", "message": repr(e)}, 500


def hide_patient(medical_insurance_id: str) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                hide_patient_query = """
                    UPDATE users SET hidden = TRUE WHERE medical_insurance_id = %s
                """
                cur.execute(hide_patient_query, (medical_insurance_id, ))

                conn.commit()

                return {"status": "success"}, 200

    except ForeignKeyViolation as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": str(e)}, 500


def get_patient_version_history(medical_insurance_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get the complete version history of a patient, showing the full patient record 
    at each point in time when a change was made to any part of the patient's data.

    Returns:
        A dictionary with a list of patient snapshots in chronological order.
    """
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                patient_check_query = """
                    SELECT COUNT(*) FROM users
                    WHERE medical_insurance_id = %s AND hidden IS NOT TRUE
                """
                cur.execute(patient_check_query, (medical_insurance_id,))
                count = cur.fetchone()[0]

                if count == 0:
                    return {"status": "error", "message": "Patient not found."}, 404

                cur.execute("""
                    SELECT user_id FROM users
                    WHERE medical_insurance_id = %s AND hidden IS NOT TRUE
                    ORDER BY modified_at DESC
                    LIMIT 1
                """, (medical_insurance_id,))
                user_id = cur.fetchone()[0]

                timestamps_query = """
                    SELECT modified_at AS timestamp FROM users
                    WHERE medical_insurance_id = %s AND hidden IS NOT TRUE

                    UNION

                    SELECT modified_at FROM coordinates
                    WHERE user_id = %s AND hidden IS NOT TRUE

                    UNION

                    SELECT modified_at FROM medical_history
                    WHERE patient_id = %s AND hidden IS NOT TRUE

                    UNION

                    SELECT modified_at FROM medical_visits
                    WHERE patient_id = %s AND hidden IS NOT TRUE

                    ORDER BY timestamp
                """
                cur.execute(timestamps_query, (medical_insurance_id, user_id,
                            medical_insurance_id, medical_insurance_id))
                timestamp_rows = cur.fetchall()

                timestamps = sorted(set(row[0] for row in timestamp_rows))

                version_map = {}

                for timestamp in timestamps:
                    snapshot = _build_patient_record_at_timestamp(
                        cur, medical_insurance_id, user_id, timestamp)
                    if snapshot:
                        ts_key = timestamp.isoformat()
                        version_map[ts_key] = snapshot

                return {"status": "success", "data": version_map}, 200

    except Exception as e:
        return {"status": "error", "message": repr(e)}, 500


def _build_patient_record_at_timestamp(cursor, medical_insurance_id: str, user_id: str, timestamp: datetime) -> Dict[str, Any]:
    """
    Helper function to build a complete patient record as it existed at a specific timestamp.
    Returns the patient record in a format compatible with PatientVersionSnapshot model.
    """
    user_query = """
        SELECT
            medical_insurance_id,
            gender,
            city_of_birth,
            user_id,
            login,
            user_type,
            first_name,
            last_name,
            phone_number,
            email,
            modified_at,
            created_at,
            date_of_birth
        FROM users
        WHERE medical_insurance_id = %s AND modified_at <= %s AND hidden IS NOT TRUE
        ORDER BY modified_at DESC
        LIMIT 1;
    """
    cursor.execute(user_query, (medical_insurance_id, timestamp))
    user_row = cursor.fetchone()

    if not user_row:
        return {
            "error": "No user row for given id",
        }

    coordinates_query = """
        SELECT DISTINCT ON (coordinate_id)
            coordinate_id,
            street_address,
            apartment,
            postal_code,
            city,
            country
        FROM coordinates
        WHERE user_id = %s AND modified_at <= %s AND hidden IS NOT TRUE
        ORDER BY coordinate_id, modified_at DESC;
    """
    cursor.execute(coordinates_query, (user_id, timestamp))
    coordinates_rows = cursor.fetchall()

    coordinates = [
        {
            "id": coord[0],
            "street_address": coord[1],
            "apartment": coord[2],
            "postal_code": coord[3],
            "city": coord[4],
            "country": coord[5]
        }
        for coord in coordinates_rows
    ]

    medical_history_query = """
        SELECT DISTINCT ON (mh.history_id)
            mh.history_id,
            mh.diagnostic,
            mh.treatment,
            d.user_id,
            d.login,
            d.user_type,
            d.first_name,
            d.last_name,
            mh.start_date,
            mh.end_date
        FROM medical_history mh
        JOIN users d ON mh.doctor_id = d.user_id
        WHERE mh.patient_id = %s AND mh.modified_at <= %s AND mh.hidden IS NOT TRUE
        ORDER BY mh.history_id, mh.modified_at DESC;
    """
    cursor.execute(medical_history_query, (medical_insurance_id, timestamp))
    medical_history_rows = cursor.fetchall()

    medical_history = []
    for mh in medical_history_rows:
        medical_history.append({
            "id": mh[0],
            "diagnostic": mh[1],
            "treatment": mh[2],
            "doctor": {
                "id": mh[3],
                "login": mh[4],
                "user_type": mh[5],
                "first_name": mh[6],
                "last_name": mh[7]
            },
            "start_date": mh[8],
            "end_date": mh[9]
        })

    medical_visits_query = """
        SELECT DISTINCT ON (mv.visit_id)
            mv.visit_id,
            mv.patient_id,
            d.user_id,
            d.login,
            d.user_type,
            d.first_name,
            d.last_name,
            mv.visit_date,
            mv.diagnostic_established,
            mv.treatment,
            mv.visit_summary,
            mv.notes,
            mv.created_at,
            e.establishment_id,
            e.establishment_name,
            e.created_at as establishment_created_at
        FROM medical_visits mv
        LEFT JOIN users d ON mv.doctor_id = d.user_id
        LEFT JOIN establishments e ON mv.establishment_id = e.establishment_id
        WHERE mv.patient_id = %s AND mv.modified_at <= %s AND mv.hidden IS NOT TRUE
        ORDER BY mv.visit_id, mv.modified_at DESC;
    """
    cursor.execute(medical_visits_query, (medical_insurance_id, timestamp))
    medical_visits_rows = cursor.fetchall()

    medical_visits = [
        {
            "id": mv[0],
            "patient_id": mv[1],
            "doctor": {
                "id": mv[2],
                "login": mv[3],
                "user_type": mv[4],
                "first_name": mv[5],
                "last_name": mv[6]
            },
            "visit_date": mv[7].isoformat() if mv[7] else None,
            "diagnostic_established": mv[8],
            "treatment": mv[9],
            "visit_summary": mv[10],
            "notes": mv[11],
            "created_at": mv[12],
            "establishment": {
                "establishment_id": mv[13],
                "establishment_name": mv[14],
                "created_at": mv[15]
            }
        }
        for mv in medical_visits_rows
    ]

    parents_query = """
                    SELECT
                        p.parent_id,
                        u.login,
                        u.user_type,
                        u.first_name,
                        u.last_name,
                        u.phone_number,
                        u.email,
                        u.created_at,
                        u.modified_at
                    FROM parents p
                    JOIN (
                        SELECT
                            *,
                            ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY modified_at DESC) AS rn
                        FROM users
                    ) u ON p.parent_id = u.user_id AND u.rn = 1
                    WHERE p.child_id = %s AND p.hidden IS NOT TRUE;
    """
    cursor.execute(parents_query, (user_id,))
    parents_rows = cursor.fetchall()

    parents = []
    for parent in parents_rows:
        parents.append({
            "parent": {
                "user_id": parent[0],
                "login": parent[1],
                "user_type": parent[2],
                "first_name": parent[3],
                "last_name": parent[4],
                "phone_number": parent[5],
                "email": parent[6],
                "created_at": parent[7],
                "modified_at": parent[8]
            }
        })

    return {
        "user_id": user_row[3],
        "login": user_row[4],
        "user_type": user_row[5],
        "first_name": user_row[6],
        "last_name": user_row[7],
        "phone_number": user_row[8],
        "email": user_row[9],
        "medical_insurance_id": user_row[0],
        "gender": user_row[1],
        "city_of_birth": user_row[2],
        "date_of_birth": user_row[12],
        "created_at": user_row[11],
        "modified_at": user_row[10],
        "coordinates": coordinates,
        "medical_history": medical_history,
        "medical_visits": medical_visits,
        "parents": parents,
        "snapshot_timestamp": timestamp
    }

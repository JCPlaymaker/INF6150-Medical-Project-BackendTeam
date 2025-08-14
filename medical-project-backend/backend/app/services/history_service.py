from typing import Dict, Any
from psycopg2.errors import ForeignKeyViolation
from ..models import HistoryCreate, HistoryUpdate, MedicalHistoryUpdateResponse, HistoryCreateResponse
from flask import current_app
from ..db import Database
from ..utils.lookup_helpers import lookup_doctor_id


def add_history(medical_insurance_id: str, data: HistoryCreate) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        doctor_id = data.doctor_id
        if not doctor_id and data.doctor_first_name and data.doctor_last_name:
            doctor_id = lookup_doctor_id(
                first_name=data.doctor_first_name,
                last_name=data.doctor_last_name
            )
            if not doctor_id:
                return {
                    "status": "error",
                    "message": f"Doctor with name {data.doctor_first_name} {data.doctor_last_name} not found"
                }, 400

        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                insert_history_query = """
                    INSERT INTO medical_history (patient_id, diagnostic,
                                                 treatment, doctor_id,
                                                 start_date, end_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING history_id;
                """
                cur.execute(insert_history_query, (
                    medical_insurance_id,
                    data.diagnostic,
                    data.treatment,
                    doctor_id,  # Use the resolved doctor_id
                    data.start_date,
                    data.end_date
                ))
                history_id = cur.fetchone()[0]

                conn.commit()

                history_response = HistoryCreateResponse(
                    history_id=history_id,
                )

                return {"status": "success", "message": history_response}, 201

    except ForeignKeyViolation:
        return {"status": "error", "message": "Invalid foreign key reference."}, 400
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


def update_history(history_id: str, data: HistoryUpdate) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_created_at_query = """
                    SELECT diagnostic, treatment, doctor_id,
                        start_date, end_date, created_at, patient_id
                    FROM medical_history
                    WHERE history_id = %s
                """
                cur.execute(select_created_at_query, (
                    history_id,
                ))
                patient_row = cur.fetchone()

                if not patient_row:
                    return {"status": "error", "message": "History not found."}, 404

                history_data = {
                    "diagnostic": patient_row[0],
                    "treatment": patient_row[1],
                    "doctor_id": patient_row[2],
                    "start_date": patient_row[3],
                    "end_date": patient_row[4],
                    "created_at": patient_row[5],
                    "patient_id": patient_row[6]
                }

                if data.diagnostic != "":
                    history_data["diagnostic"] = data.diagnostic

                if data.treatment != "":
                    history_data["treatment"] = data.treatment

                if data.doctor_id != "":
                    history_data["doctor_id"] = data.doctor_id

                if data.start_date != "":
                    history_data["start_date"] = data.start_date

                if data.end_date != "":
                    history_data["end_date"] = data.end_date

                insert_history_query = """
                    INSERT INTO medical_history (history_id, patient_id,
                                                 diagnostic,
                                                 treatment, doctor_id,
                                                 start_date, end_date,
                                                 created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """
                cur.execute(insert_history_query, (
                    history_id,
                    history_data["patient_id"],
                    history_data["diagnostic"],
                    history_data["treatment"],
                    history_data["doctor_id"],
                    history_data["start_date"],
                    history_data["end_date"],
                    history_data["created_at"],
                ))

                conn.commit()

        history_response = MedicalHistoryUpdateResponse(
            patient_id=history_data["patient_id"],
            history_id=history_id,
            diagnostic=history_data["diagnostic"],
            treatment=history_data["treatment"],
            doctor_id=history_data["doctor_id"],
            start_date=history_data["start_date"],
            end_date=history_data["end_date"],
        )
        return {"status": "success", "data": history_response}, 201

    except ForeignKeyViolation:
        raise ForeignKeyViolation("Invalid foreign key reference.")
    except Exception as e:
        raise e


def hide_history(history_id: str) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                hide_history_query = """
                    UPDATE medical_history SET hidden = TRUE
                    WHERE history_id = %s
                """
                cur.execute(hide_history_query, (history_id, ))

                conn.commit()

                return {"status": "success"}, 200

    except ForeignKeyViolation as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": str(e)}, 500

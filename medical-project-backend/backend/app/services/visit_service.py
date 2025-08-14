from typing import Dict, Any
from psycopg2.errors import ForeignKeyViolation
from ..models import VisitCreate, VisitUpdate, VisitUpdateResponse, VisitCreateResponse
from flask import current_app
from ..db import Database
from ..utils.lookup_helpers import lookup_doctor_id, lookup_establishment_id


def add_visit(medical_insurance_id: str, data: VisitCreate) -> tuple[Dict[str, Any], int]:
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

        establishment_id = data.establishment_id
        if not establishment_id and data.establishment_name:
            establishment_id = lookup_establishment_id(
                establishment_name=data.establishment_name
            )
            if not establishment_id:
                return {
                    "status": "error",
                    "message": f"Establishment with name '{data.establishment_name}' not found"
                }, 400

        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                insert_visit_query = """
                    INSERT INTO medical_visits (patient_id, establishment_id,
                                                doctor_id, visit_date,
                                                diagnostic_established,
                                                treatment, visit_summary,
                                                notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING visit_id;
                """
                cur.execute(insert_visit_query, (
                    medical_insurance_id,
                    establishment_id,  # Use the resolved establishment_id
                    doctor_id,  # Use the resolved doctor_id
                    data.visit_date,
                    data.diagnostic,
                    data.treatment,
                    data.summary,
                    data.notes
                ))
                visit_id = cur.fetchone()[0]

                if not visit_id:
                    return {
                        "status": "error",
                        "message": "Doctor or Establishment not found"
                    }, 400

                conn.commit()

                visit_response = VisitCreateResponse(
                    visit_id=visit_id,
                )

                return {"status": "success", "message": visit_response}, 201

    except ForeignKeyViolation:
        return {"status": "error", "message": "Invalid foreign key reference."}, 400
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


def update_visit(visit_id: str, data: VisitUpdate) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                select_created_at_query = """
                    SELECT establishment_id, doctor_id, visit_date,
                        diagnostic_established, treatment, visit_summary,
                        notes, created_at, patient_id
                    FROM medical_visits
                    WHERE visit_id = %s
                """
                cur.execute(select_created_at_query, (
                    visit_id,
                ))
                visit_row = cur.fetchone()

                if not visit_row:
                    return {"status": "error", "message": "Visit not found."}, 404

                visit_data = {
                    "establishment_id": visit_row[0],
                    "doctor_id": visit_row[1],
                    "visit_date": visit_row[2],
                    "diagnostic": visit_row[3],
                    "treatment": visit_row[4],
                    "summary": visit_row[5],
                    "notes": visit_row[6],
                    "created_at": visit_row[7],
                    "patient_id": visit_row[8]
                }

                if data.establishment_id != "":
                    visit_data["establishment_id"] = data.establishment_id

                if data.doctor_id != "":
                    visit_data["doctor_id"] = data.doctor_id

                if data.visit_date != "":
                    visit_data["visit_date"] = data.visit_date

                if data.diagnostic != "":
                    visit_data["diagnostic"] = data.diagnostic

                if data.treatment != "":
                    visit_data["treatment"] = data.treatment

                if data.summary != "":
                    visit_data["summary"] = data.summary

                if data.notes != "":
                    visit_data["notes"] = data.notes

                insert_visit_query = """
                    INSERT INTO medical_visits (visit_id,
                                                 patient_id, establishment_id,
                                                 doctor_id, visit_date,
                                                 diagnostic_established,
                                                 treatment, visit_summary,
                                                 notes, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING modified_at;
                """
                cur.execute(insert_visit_query, (
                    visit_id,
                    visit_data["patient_id"],
                    visit_data["establishment_id"],
                    visit_data["doctor_id"],
                    visit_data["visit_date"],
                    visit_data["diagnostic"],
                    visit_data["treatment"],
                    visit_data["summary"],
                    visit_data["notes"],
                    visit_data["created_at"],
                ))

                conn.commit()

        visit_response = VisitUpdateResponse(
            patient_id=visit_data["patient_id"],
            visit_id=visit_id,
            establishment_id=visit_data["establishment_id"],
            doctor_id=visit_data["doctor_id"],
            visit_date=visit_data["visit_date"],
            diagnostic=visit_data["diagnostic"],
            treatment=visit_data["treatment"],
            summary=visit_data["summary"],
            notes=visit_data["notes"],
            created_at=visit_data["created_at"]
        )
        return {"status": "success", "data": visit_response}, 201

    except ForeignKeyViolation:
        raise ForeignKeyViolation("Invalid foreign key reference.")
    except Exception as e:
        raise e


def hide_visit(visit_id: str) -> tuple[Dict[str, Any], int]:
    db_instance: Database = current_app.config['DATABASE']
    try:
        with db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                hide_visit_query = """
                    UPDATE medical_visits SET hidden = TRUE
                    WHERE visit_id = %s
                """
                cur.execute(hide_visit_query, (visit_id, ))

                conn.commit()

                return {"status": "success"}, 200

    except ForeignKeyViolation as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": str(e)}, 500

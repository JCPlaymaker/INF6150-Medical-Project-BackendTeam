import psycopg2.pool
import os
from pathlib import Path
from dotenv import load_dotenv
from contextlib import contextmanager
import bcrypt
from .schemas import (
    CREATE_COORDINATES_TABLE,
    CREATE_EXTENSION_UUID,
    CREATE_HISTORY_ID_INDEX,
    CREATE_USER_ID_INDEX,
    CREATE_VISIT_ID_INDEX,
    DROP_COORDINATES_TABLE,
    CREATE_MEDICAL_HISTORY_TABLE,
    DROP_MEDICAL_HISTORY_TABLE,
    CREATE_MEDICAL_VISITS_TABLE,
    DROP_MEDICAL_VISITS_TABLE,
    CREATE_USERS_TABLE,
    DROP_USERS_TABLE,
    CREATE_USER_TYPE_ENUM,
    DROP_USER_TYPE_ENUM,
    CREATE_PARENTS_TABLE,
    DROP_PARENTS_TABLE,
    CREATE_COORDINATE_ID_INDEX,
    CREATE_MEDICAL_INSURANCE_ID_INDEX,
    DROP_COORDINATE_ID_INDEX,
    DROP_MEDICAL_INSURANCE_ID_INDEX,
    DROP_USER_ID_INDEX,
    DROP_VISIT_ID_INDEX,
    DROP_HISTORY_ID_INDEX,
    CREATE_ESTABLISHMENTS_TABLE,
    DROP_ESTABLISHMENTS_TABLE,
    CREATE_JTI_INDEX,
    DROP_JTI_INDEX,
    CREATE_USER_BLACKLIST_INDEX,
    DROP_USER_BLACKLIST_INDEX,
    CREATE_TOKEN_BLACKLIST_TABLE,
    DROP_TOKEN_BLACKLIST_TABLE,
    CREATE_MFA_CONFIG_TABLE,
    DROP_MFA_CONFIG_TABLE,
    CREATE_MFA_CONFIG_INDEX,
    DROP_MFA_CONFIG_INDEX
)
import json


class Database:
    def __init__(self,
                 user=None,
                 password=None,
                 host=None,
                 port=None,
                 database=None):
        load_dotenv()

        self.user = user or os.getenv("INF6150_DATABASE_USER")
        self.password = password or os.getenv("INF6150_DATABASE_PASSWORD")

        in_container = os.getenv(
            "INF6150_SERVER_IN_CONTAINER", 'True').lower() in ('true', '1', 't')
        if in_container:
            self.host = host or os.getenv("INF6150_DATABASE_DOCKER_HOST")
            self.port = port or os.getenv("INF6150_DATABASE_DOCKER_PORT")
        else:
            self.host = host or os.getenv("INF6150_DATABASE_HOST")
            self.port = port or os.getenv("INF6150_DATABASE_PORT")

        self.database = database or os.getenv("INF6150_DATABASE_NAME")

        if not all([self.user, self.password, self.host, self.port, self.database]):
            raise ValueError(
                "One or more required database environment variables are not set.")

        self.pool = psycopg2.pool.SimpleConnectionPool(
            1,
            20,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )

        if not self.pool:
            raise Exception("Connection pool could not be established.")
        print("Database connection pool created successfully.")

    @contextmanager
    def get_conn(self):
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    def initialize_extensions(self):
        queries = [
            CREATE_EXTENSION_UUID
        ]
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                for query in queries:
                    cur.execute(query)
            conn.commit()
        print("All extensions have been initialized.")

    def initialize_tables(self):
        queries = [
            CREATE_USER_TYPE_ENUM,
            CREATE_ESTABLISHMENTS_TABLE,
            CREATE_USERS_TABLE,
            CREATE_COORDINATES_TABLE,
            CREATE_MEDICAL_HISTORY_TABLE,
            CREATE_MEDICAL_VISITS_TABLE,
            CREATE_PARENTS_TABLE,
            CREATE_TOKEN_BLACKLIST_TABLE,
            CREATE_MFA_CONFIG_TABLE
        ]
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                for query in queries:
                    cur.execute(query)
            conn.commit()
        print("All tables have been initialized.")

    def initialize_indexes(self):
        queries = [
            CREATE_USER_ID_INDEX,
            CREATE_MEDICAL_INSURANCE_ID_INDEX,
            CREATE_COORDINATE_ID_INDEX,
            CREATE_VISIT_ID_INDEX,
            CREATE_HISTORY_ID_INDEX,
            CREATE_JTI_INDEX,
            CREATE_USER_BLACKLIST_INDEX,
            CREATE_MFA_CONFIG_INDEX
        ]
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                for query in queries:
                    cur.execute(query)
            conn.commit()
        print("All indexes have been initialized.")

    def drop_tables(self, log: bool = True):
        queries = [
            DROP_PARENTS_TABLE,
            DROP_MEDICAL_VISITS_TABLE,
            DROP_MEDICAL_HISTORY_TABLE,
            DROP_COORDINATES_TABLE,
            DROP_USERS_TABLE,
            DROP_ESTABLISHMENTS_TABLE,
            DROP_TOKEN_BLACKLIST_TABLE,
            DROP_USER_TYPE_ENUM,
            DROP_MFA_CONFIG_TABLE
        ]
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                for query in queries:
                    cur.execute(query)
            conn.commit()
        if log:
            print("All tables have been dropped.")

    def drop_indexes(self, log: bool = True):
        queries = [
            DROP_USER_ID_INDEX,
            DROP_MEDICAL_INSURANCE_ID_INDEX,
            DROP_COORDINATE_ID_INDEX,
            DROP_VISIT_ID_INDEX,
            DROP_HISTORY_ID_INDEX,
            DROP_JTI_INDEX,
            DROP_USER_BLACKLIST_INDEX,
            DROP_MFA_CONFIG_INDEX
        ]
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                for query in queries:
                    cur.execute(query)
            conn.commit()
        if log:
            print("All indexes have been dropped.")

    def add_test_data(self, data_path: str):
        with open(data_path, 'r') as f:
            records = json.load(f)

        table_name = Path(data_path).stem

        with self.get_conn() as conn:
            with conn.cursor() as cur:
                if table_name == "users":
                    for record in records:
                        password_bytes = record["password"].encode('utf-8')
                        salt = bcrypt.gensalt()
                        pwhash = bcrypt.hashpw(password_bytes, salt)
                        password_hash = pwhash.decode('utf8')
                        cur.execute("""
                            INSERT INTO users (user_id, medical_insurance_id, login, password_hash, user_type, first_name, last_name, phone_number, email, gender, city_of_birth, date_of_birth)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """, (
                            record.get("user_id"),
                            record.get("medical_insurance_id"),
                            record["login"],
                            password_hash,
                            record["user_type"],
                            record["first_name"],
                            record["last_name"],
                            record["phone_number"],
                            record["email"],
                            record.get("gender"),
                            record.get("city_of_birth"),
                            record.get("date_of_birth")
                        ))
                elif table_name == "coordinates":
                    for record in records:
                        cur.execute("""
                            INSERT INTO coordinates (coordinate_id, user_id, street_address, apartment, postal_code, city, country)
                            VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """, (
                            record.get("coordinate_id"),
                            record["user_id"],
                            record["street_address"],
                            record.get("apartment"),
                            record["postal_code"],
                            record["city"],
                            record["country"]
                        ))
                elif table_name == "medical_history":
                    for record in records:
                        cur.execute("""
                            INSERT INTO medical_history (history_id, patient_id, diagnostic, treatment, doctor_id, start_date, end_date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """, (
                            record.get("history_id"),
                            record["patient_id"],
                            record["diagnostic"],
                            record["treatment"],
                            record["doctor_id"],
                            record.get("start_date"),
                            record.get("end_date")
                        ))
                elif table_name == "medical_visits":
                    for record in records:
                        cur.execute("""
                        INSERT INTO medical_visits (
                            visit_id, patient_id, establishment_id, doctor_id,
                            visit_date, diagnostic_established, treatment,
                            visit_summary, notes
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """, (
                            record.get("visit_id"),
                            record["patient_id"],
                            record["establishment_id"],
                            record["doctor_id"],
                            record["visit_date"],
                            record.get("diagnostic_established"),
                            record.get("treatment"),
                            record["visit_summary"],
                            record.get("notes")
                        ))
                elif table_name == "establishments":
                    for record in records:
                        cur.execute("""
                        INSERT INTO establishments (establishment_id, establishment_name)
                        VALUES (%s, %s);
                    """, (
                            record.get("establishment_id"),
                            record["establishment_name"]
                        ))
                elif table_name == "parents":
                    for record in records:
                        cur.execute("""
                            INSERT INTO parents (parent_id, child_id)
                            VALUES (%s, %s)
                            ON CONFLICT (parent_id, child_id) DO NOTHING;
                        """, (
                            record["parent_id"],
                            record["child_id"]
                        ))
                else:
                    print(f"Unknown table name '{table_name}' in data file '{data_path}'."
                          " Skipping.")
                    return
            conn.commit()
        print(f"Test data from '{data_path}' has been added.")

    def close_pool(self):
        self.pool.closeall()
        print("Database connection pool has been closed.")

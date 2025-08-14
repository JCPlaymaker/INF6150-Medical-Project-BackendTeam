import os
import sys
import time
from dotenv import load_dotenv
from app.db import Database


def run_tests():
    """
    Set up the test framework and run all registered tests with optimized performance.
    This function is called by the main CLI.
    """
    try:
        print("Inside run_tests function...")

        load_dotenv()
        print("Environment variables loaded")

        # Get database connection parameters from environment variables
        user = os.getenv("INF6150_TEST_DATABASE_USER")
        password = os.getenv("INF6150_TEST_DATABASE_PASSWORD")

        in_container = os.getenv(
            "INF6150_SERVER_IN_CONTAINER", 'True').lower() in ('true', '1', 't')
        if in_container:
            host = os.getenv("INF6150_TEST_DATABASE_DOCKER_HOST")
            port = os.getenv("INF6150_TEST_DATABASE_DOCKER_PORT")
        else:
            host = os.getenv("INF6150_TEST_DATABASE_HOST")
            port = os.getenv("INF6150_TEST_DATABASE_PORT")

        database = os.getenv("INF6150_TEST_DATABASE_NAME")
        api_port = os.getenv("INF6150_API_PORT")

        print(f"Database config: {user}@{host}:{port}/{database}")
        print(f"API port: {api_port}")

        if api_port is None:
            print("Error: INF6150_API_PORT environment variable not set.")
            sys.exit(1)

        print("Importing test modules...")

        from tests.test_framework import TestFramework

        from tests.api_tests import register_tests as register_api_tests
        from tests.user_tests import register_tests as register_user_tests
        from tests.enhanced_users_tests import register_tests as register_enhanced_user_tests
        from tests.patients_tests import register_tests as register_patients_tests
        from tests.jwt_tests import register_tests as register_jwt_tests
        from tests.medical_history_tests import register_tests as register_medical_history_tests
        from tests.medical_visits_tests import register_tests as register_medical_visits_tests
        from tests.service_tests import register_tests as register_service_tests
        from tests.versioning_tests import register_tests as register_versioning_tests
        from tests.doctor_tests import register_tests as register_doctor_tests
        from tests.establishment_tests import register_tests as register_establishment_tests
        from tests.lookup_alt_tests import register_tests as register_lookup_alt_tests
        from tests.coordinate_tests import register_tests as register_coordinate_tests
        from tests.parents_tests import register_tests as register_parents_tests
        from tests.credentials_tests import register_tests as register_credentials_tests
        from tests.deletion_tests import register_tests as register_deletion_tests
        from tests.mfa_tests import register_tests as register_mfa_tests

        print("All modules imported successfully")

        print("Creating database connection...")
        db = Database(user, password, host, port, database)
        print("Database connected")

        print("Creating test framework...")
        test_framework = TestFramework(db, api_port)
        print("Test framework created")

        test_framework.use_transactions = True

        start_time = time.time()

        print("Creating test suites...")
        api_suite = test_framework.create_suite("API Tests")
        basic_user_suite = test_framework.create_suite("User Tests")
        enhanced_user_suite = test_framework.create_suite(
            "User Tests")
        patients_suite = test_framework.create_suite("Patient Tests")
        jwt_suite = test_framework.create_suite("JWT Authentication Tests")
        medical_history_suite = test_framework.create_suite(
            "Medical History Tests")
        medical_visits_suite = test_framework.create_suite(
            "Medical Visits Tests")
        service_suite = test_framework.create_suite("Service Behavior Tests")
        versioning_suite = test_framework.create_suite("Versioning Tests")
        doctor_suite = test_framework.create_suite("Doctor API Tests")
        establishment_suite = test_framework.create_suite(
            "Establishment API Tests")
        lookup_alt_suite = test_framework.create_suite(
            "Lookup Alt Tests")
        coordinate_suite = test_framework.create_suite("Coordinate Tests")
        parents_suite = test_framework.create_suite(
            "Parents Relationship Tests")
        credentials_suite = test_framework.create_suite(
            "Credentials Update Tests")
        deletion_suite = test_framework.create_suite("Deletion/Hiding Tests")
        mfa_suite = test_framework.create_suite("MFA Tests")

        # Register tests with each suite
        print("Registering tests...")
        register_api_tests(api_suite, test_framework)
        register_user_tests(basic_user_suite, test_framework)
        register_enhanced_user_tests(enhanced_user_suite, test_framework)
        register_patients_tests(patients_suite, test_framework)
        register_jwt_tests(jwt_suite, test_framework)
        register_medical_history_tests(medical_history_suite, test_framework)
        register_medical_visits_tests(medical_visits_suite, test_framework)
        register_service_tests(service_suite, test_framework)
        register_versioning_tests(versioning_suite, test_framework)
        register_doctor_tests(doctor_suite, test_framework)
        register_establishment_tests(establishment_suite, test_framework)
        register_lookup_alt_tests(lookup_alt_suite, test_framework)
        register_coordinate_tests(coordinate_suite, test_framework)
        register_parents_tests(parents_suite, test_framework)
        register_credentials_tests(credentials_suite, test_framework)
        register_deletion_tests(deletion_suite, test_framework)
        register_mfa_tests(mfa_suite, test_framework)

        print("Running all tests...")
        test_framework.run_all_tests()

        if '--cleanup' in sys.argv:
            print("Cleanup flag detected, cleaning up database...")
            test_framework.cleanup_database()

        end_time = time.time()
        total_time = end_time - start_time
        print(f"\nTotal execution time (including setup): {
              total_time:.2f} seconds")

    except Exception as e:
        print(f"ERROR in test runner: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

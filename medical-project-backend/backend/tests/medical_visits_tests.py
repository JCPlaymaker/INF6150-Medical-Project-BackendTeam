import requests
from datetime import date, datetime


def register_tests(suite, test_framework):
    """Register medical visits-related tests with the provided test suite"""

    @suite.setup
    def setup_medical_visits_tests(test_framework):
        """Setup tokens for testing medical visits endpoints"""
        # Database setup now handled at framework level with transactions

        try:
            # Get admin token for admin-only operations
            admin_token = test_framework.login_and_get_token(
                email="carol.williams@example.com",
                password="password5"
            )
            test_framework.admin_token = admin_token

            # Get doctor token for doctor operations
            doctor_token = test_framework.login_and_get_token(
                email="alice.brown@example.com",
                password="password3"
            )
            test_framework.doctor_token = doctor_token

            # Get patient token to test permission restrictions
            patient_token = test_framework.login_and_get_token(
                email="john.doe@example.com",
                password="password1"
            )
            test_framework.patient_token = patient_token
        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_create_medical_visit_as_doctor(test_framework):
        """Test creating a new medical visit record as a doctor"""
        # Create a medical visit record
        new_visit = {
            # Using existing establishment ID from test data
            "establishment_id": "e1234567-89ab-cdef-0123-456789abcdef",
            # Using existing doctor ID from test data
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "visit_date": date.today().isoformat(),
            "diagnostic": "Test Visit Diagnosis",
            "treatment": "Test Visit Treatment",
            "summary": "Test visit summary",
            "notes": "Additional test notes"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/visits",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_visit
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create medical visit: {
                                 response.status_code}, {response.text}")

        # Verify response contains the created visit ID
        data = response.json()
        if "visit_id" not in data:
            raise AssertionError(f"Response does not contain visit_id: {data}")

        # Store created visit ID for later tests
        test_framework.created_visit_id = data["visit_id"]

    @suite.test
    def test_create_medical_visit_as_admin(test_framework):
        """Test creating a new medical visit record as an admin"""
        new_visit = {
            "establishment_id": "e2345678-89ab-cdef-0123-456789abcdef",  # Different establishment
            "doctor_id": "aa57295e-fa4f-4821-b04c-711ea0be487a",  # Different doctor
            "visit_date": date.today().isoformat(),
            "diagnostic": "Admin Created Visit",
            "treatment": "Admin Created Treatment",
            "summary": "Admin created this visit summary",
            "notes": "Admin notes"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/visits",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_visit
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create medical visit as admin: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_create_medical_visit_as_patient_denied(test_framework):
        """Test that patients cannot create medical visit records"""
        new_visit = {
            "establishment_id": "e1234567-89ab-cdef-0123-456789abcdef",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "visit_date": date.today().isoformat(),
            "diagnostic": "Patient Created Visit",
            "treatment": "Patient Created Treatment",
            "summary": "Patient created this visit summary",
            "notes": "Patient notes"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/visits",
            headers={"Authorization": f"Bearer {
                test_framework.patient_token}"},
            json=new_visit
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied with 403, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_update_medical_visit(test_framework):
        """Test updating an existing medical visit record"""
        # First create a visit to update
        new_visit = {
            "establishment_id": "e1234567-89ab-cdef-0123-456789abcdef",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "visit_date": date.today().isoformat(),
            "diagnostic": "Initial Diagnosis",
            "treatment": "Initial Treatment",
            "summary": "Initial summary",
            "notes": "Initial notes"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/visits",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_visit
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create visit for update test: {
                                 response.status_code}, {response.text}")

        visit_id = response.json()["visit_id"]

        # Now update the visit
        update_data = {
            "establishment_id": "e3456789-89ab-cdef-0123-456789abcdef",  # Change establishment
            "doctor_id": "31870799-6214-4639-a6a8-412f8e3bb232",  # Change doctor
            "visit_date": date.today().isoformat(),
            "diagnostic": "Updated Visit Diagnosis",
            "treatment": "Updated Visit Treatment",
            "summary": "Updated visit summary",
            "notes": "Updated test notes"
        }

        response = requests.put(
            f"http://localhost:{
                test_framework.api_port}/api/patients/INS123456/visits/{visit_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=update_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to update medical visit: {
                                 response.status_code}, {response.text}")

        # Verify updated data in response
        data = response.json()
        if data.get("diagnostic") != "Updated Visit Diagnosis":
            raise AssertionError(
                f"Updated diagnostic not reflected in response: {data}")

    @suite.test
    def test_create_medical_visit_validation_error(test_framework):
        """Test validation errors when creating a medical visit record"""
        # Missing required fields
        invalid_visit = {
            "establishment_id": "e1234567-89ab-cdef-0123-456789abcdef",
            # Missing doctor_id, summary, etc.
            "visit_date": date.today().isoformat()
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/visits",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=invalid_visit
        )

        # Should get 400 Bad Request
        if response.status_code != 400:
            raise AssertionError(f"Expected validation error with 400, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_update_nonexistent_visit(test_framework):
        """Test updating a non-existent medical visit record"""
        nonexistent_id = "00000000-0000-0000-0000-000000000000"  # Non-existent UUID

        update_data = {
            "establishment_id": "e1234567-89ab-cdef-0123-456789abcdef",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "visit_date": date.today().isoformat(),
            "diagnostic": "Updated Visit Diagnosis",
            "treatment": "Updated Visit Treatment",
            "summary": "Updated visit summary",
            "notes": "Updated test notes"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/visits/{
                nonexistent_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=update_data
        )

        # Should get 404 Not Found or 500 Internal Server Error depending on implementation
        if response.status_code not in [404, 500]:
            raise AssertionError(f"Expected error when updating non-existent visit, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_create_visit_with_invalid_foreign_keys(test_framework):
        """Test creating a visit with invalid foreign keys (doctor_id, establishment_id)"""
        new_visit = {
            # Non-existent establishment
            "establishment_id": "ffffffff-ffff-ffff-ffff-ffffffffffff",
            "doctor_id": "ffffffff-ffff-ffff-ffff-ffffffffffff",  # Non-existent doctor
            "visit_date": date.today().isoformat(),
            "diagnostic": "Invalid FK Test",
            "treatment": "Test Treatment",
            "summary": "Testing foreign key constraints",
            "notes": "Should fail with appropriate error"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/visits",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_visit
        )

        # Should get an error due to foreign key constraints
        if response.status_code not in [400, 500]:
            raise AssertionError(f"Expected error for invalid foreign keys, but got {
                                 response.status_code}: {response.text}")

    @suite.teardown
    def teardown_medical_visits_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

import requests
from datetime import date, datetime


def register_tests(suite, test_framework):
    """Register medical history-related tests with the provided test suite"""

    @suite.setup
    def setup_medical_history_tests(test_framework):
        """Setup tokens for testing medical history endpoints"""
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
    def test_create_medical_history_as_doctor(test_framework):
        """Test creating a new medical history record as a doctor"""
        # Create a medical history record
        new_history = {
            "diagnostic": "Test Condition",
            "treatment": "Test Treatment",
            # Using existing doctor ID from test data
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": date.today().isoformat(),
            "end_date": None
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/history",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_history
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create medical history: {
                                 response.status_code}, {response.text}")

        # Verify response contains the created history ID
        data = response.json()
        if "history_id" not in data:
            raise AssertionError(
                f"Response does not contain history_id: {data}")

        # Store created history ID for later tests
        test_framework.created_history_id = data["history_id"]

    @suite.test
    def test_create_medical_history_as_admin(test_framework):
        """Test creating a new medical history record as an admin"""
        new_history = {
            "diagnostic": "Admin Created Condition",
            "treatment": "Admin Created Treatment",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": date.today().isoformat(),
            "end_date": None
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/history",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_history
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create medical history as admin: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_create_medical_history_as_patient_denied(test_framework):
        """Test that patients cannot create medical history records"""
        new_history = {
            "diagnostic": "Patient Created Condition",
            "treatment": "Patient Created Treatment",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": date.today().isoformat(),
            "end_date": None
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/history",
            headers={"Authorization": f"Bearer {
                test_framework.patient_token}"},
            json=new_history
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied with 403, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_update_medical_history(test_framework):
        """Test updating an existing medical history record"""
        # First create a history to update
        new_history = {
            "diagnostic": "Initial Condition",
            "treatment": "Initial Treatment",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": date.today().isoformat(),
            "end_date": None
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/history",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_history
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create history for update test: {
                                 response.status_code}, {response.text}")

        history_id = response.json()["history_id"]

        # Now update it
        update_data = {
            "diagnostic": "Updated Test Condition",
            "treatment": "Updated Test Treatment",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": date.today().isoformat(),
            "end_date": date.today().isoformat()  # Set an end date
        }

        response = requests.put(
            f"http://localhost:{
                test_framework.api_port}/api/patients/INS123456/history/{history_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=update_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to update medical history: {
                                 response.status_code}, {response.text}")

        # Verify updated data in response
        data = response.json()
        if data.get("diagnostic") != "Updated Test Condition":
            raise AssertionError(
                f"Updated diagnostic not reflected in response: {data}")

    @suite.test
    def test_create_medical_history_validation_error(test_framework):
        """Test validation errors when creating a medical history record"""
        # Missing required fields
        invalid_history = {
            "diagnostic": "Test Condition",
            # Missing treatment and doctor_id
            "start_date": date.today().isoformat()
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/history",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=invalid_history
        )

        # Should get 400 Bad Request
        if response.status_code != 400:
            raise AssertionError(f"Expected validation error with 400, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_update_nonexistent_history(test_framework):
        """Test updating a non-existent medical history record"""
        nonexistent_id = "00000000-0000-0000-0000-000000000000"  # Non-existent UUID

        update_data = {
            "diagnostic": "Updated Diagnostic",
            "treatment": "Updated Treatment",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": date.today().isoformat(),
            "end_date": date.today().isoformat()
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/history/{
                nonexistent_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=update_data
        )

        # Should get 404 Not Found or 500 Internal Server Error depending on implementation
        if response.status_code not in [404, 500]:
            raise AssertionError(f"Expected error when updating non-existent history, but got {
                                 response.status_code}: {response.text}")

    @suite.teardown
    def teardown_medical_history_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

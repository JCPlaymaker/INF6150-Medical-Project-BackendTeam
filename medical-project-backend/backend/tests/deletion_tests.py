import requests
from datetime import datetime, date


def register_tests(suite, test_framework):
    """Register tests for deletion/hiding functionality across different object types"""

    @suite.setup
    def setup_deletion_tests(test_framework):
        """Setup tokens for testing deletion/hiding functionality"""
        try:
            # Get admin token for admin operations
            admin_token = test_framework.login_and_get_token(
                email="carol.williams@example.com",
                password="password5"
            )
            test_framework.admin_token = admin_token

            # Get doctor token
            doctor_token = test_framework.login_and_get_token(
                email="alice.brown@example.com",
                password="password3"
            )
            test_framework.doctor_token = doctor_token

            # Get patient token
            patient_token = test_framework.login_and_get_token(
                email="john.doe@example.com",
                password="password1"
            )
            test_framework.patient_token = patient_token

            # Get healthcare professional token
            healthcare_token = test_framework.login_and_get_token(
                email="david.miller@example.com",
                password="password6"
            )
            test_framework.healthcare_token = healthcare_token

            # Store test ids
            test_framework.john_doe_insurance = "INS123456"

        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_hide_patient(test_framework):
        """Test hiding a patient"""
        # First create a test patient
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_patient = {
            "login": f"deletepatient{timestamp}",
            "password": "testpassword",
            "user_type": "PATIENT",
            "first_name": "Delete",
            "last_name": "Patient",
            "phone_number": "555-123-4567",
            "email": f"deletepatient{timestamp}@example.com",
            "medical_insurance_id": f"DINS{timestamp}",
            "gender": "Male",
            "city_of_birth": "Delete City",
            "date_of_birth": "1990-01-01",
            "coordinates": [
                {
                    "street_address": "123 Delete St",
                    "postal_code": "12345",
                    "city": "Delete City",
                    "country": "Test Country"
                }
            ]
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_patient
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create patient for deletion test: {
                                 response.status_code}, {response.text}")

        insurance_id = f"DINS{timestamp}"

        # Verify patient exists
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/{insurance_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get patient before deletion: {
                                 response.status_code}, {response.text}")

        # Now hide the patient
        response = requests.delete(
            f"http://localhost:{test_framework.api_port}/api/patients/{insurance_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to hide patient: {
                                 response.status_code}, {response.text}")

        # Verify patient is hidden
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/{insurance_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        # Should get 404 Not Found
        if response.status_code != 404:
            raise AssertionError(f"Hidden patient still accessible, expected 404 but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_hide_user(test_framework):
        """Test hiding a user"""
        # First create a test user
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_user = {
            "login": f"deleteuser{timestamp}",
            "password": "testpassword",
            "user_type": "HEALTHCARE PROFESSIONAL",
            "first_name": "Delete",
            "last_name": "User",
            "phone_number": "555-987-6543",
            "email": f"deleteuser{timestamp}@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_user
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create user for deletion test: {
                                 response.status_code}, {response.text}")

        user_id = response.json()["user_id"]

        # Verify user exists
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/users/{user_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get user before deletion: {
                                 response.status_code}, {response.text}")

        # Now hide the user
        response = requests.delete(
            f"http://localhost:{test_framework.api_port}/api/users/{user_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to hide user: {
                                 response.status_code}, {response.text}")

        # Verify user is hidden
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/users/{user_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        # Should get 404 Not Found
        if response.status_code != 404:
            raise AssertionError(f"Hidden user still accessible, expected 404 but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_hide_medical_history(test_framework):
        """Test hiding a medical history record"""
        # First create a medical history record
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_history = {
            "diagnostic": f"Delete Diagnostic {timestamp}",
            "treatment": f"Delete Treatment {timestamp}",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": date.today().isoformat(),
            "end_date": None
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/{
                test_framework.john_doe_insurance}/history",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_history
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create medical history for deletion test: {
                                 response.status_code}, {response.text}")

        history_id = response.json()["history_id"]

        # Verify history exists via patient data
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/{
                test_framework.john_doe_insurance}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get patient data before history deletion: {
                                 response.status_code}, {response.text}")

        patient_data = response.json()
        history_ids = [hist["id"] for hist in patient_data["medical_history"]]

        if history_id not in history_ids:
            raise AssertionError(
                f"Created history record not found in patient data")

        # Now hide the history record
        response = requests.delete(
            f"http://localhost:{test_framework.api_port}/api/history/{history_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to hide medical history: {
                                 response.status_code}, {response.text}")

        # Verify history is hidden
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/{
                test_framework.john_doe_insurance}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get patient data after history deletion: {
                                 response.status_code}, {response.text}")

        patient_data = response.json()
        history_ids = [hist["id"] for hist in patient_data["medical_history"]]

        if history_id in history_ids:
            raise AssertionError(
                f"Hidden history record still appears in patient data")

    @suite.test
    def test_hide_medical_visit(test_framework):
        """Test hiding a medical visit record"""
        # First create a medical visit
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_visit = {
            "establishment_id": "e1234567-89ab-cdef-0123-456789abcdef",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "visit_date": date.today().isoformat(),
            "diagnostic": f"Delete Visit Diagnostic {timestamp}",
            "treatment": f"Delete Visit Treatment {timestamp}",
            "summary": f"Visit for deletion test {timestamp}",
            "notes": "Test notes"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/{
                test_framework.john_doe_insurance}/visits",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_visit
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create medical visit for deletion test: {
                                 response.status_code}, {response.text}")

        visit_id = response.json()["visit_id"]

        # Verify visit exists via patient data
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/{
                test_framework.john_doe_insurance}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get patient data before visit deletion: {
                                 response.status_code}, {response.text}")

        patient_data = response.json()
        visit_ids = [visit["id"] for visit in patient_data["medical_visits"]]

        if visit_id not in visit_ids:
            raise AssertionError(
                f"Created visit record not found in patient data")

        # Now hide the visit
        response = requests.delete(
            f"http://localhost:{test_framework.api_port}/api/visits/{visit_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to hide medical visit: {
                                 response.status_code}, {response.text}")

        # Verify visit is hidden
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/{
                test_framework.john_doe_insurance}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get patient data after visit deletion: {
                                 response.status_code}, {response.text}")

        patient_data = response.json()
        visit_ids = [visit["id"] for visit in patient_data["medical_visits"]]

        if visit_id in visit_ids:
            raise AssertionError(
                f"Hidden visit record still appears in patient data")

    @suite.test
    def test_hide_establishment(test_framework):
        """Test hiding an establishment"""
        # Create establishment or use existing one
        # Ideally, we would create a new one, but for simplicity we'll use an existing one

        # Get all establishments
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/establishments",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get establishments: {
                                 response.status_code}, {response.text}")

        establishments = response.json()["data"]

        if not establishments:
            raise AssertionError("No establishments found for testing")

        # Use the last establishment (less likely to be referenced elsewhere)
        establishment_id = establishments[-1]["establishment_id"]

        # Hide the establishment
        response = requests.delete(
            f"http://localhost:{test_framework.api_port}/api/establishments/{
                establishment_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to hide establishment: {
                                 response.status_code}, {response.text}")

        # Verify establishment is hidden
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/establishments",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get establishments after hiding: {
                                 response.status_code}, {response.text}")

        establishments_after = response.json()["data"]
        establishment_ids_after = [est["establishment_id"]
                                   for est in establishments_after]

        if establishment_id in establishment_ids_after:
            raise AssertionError(
                f"Hidden establishment still appears in establishments list")

    @suite.test
    def test_hide_as_patient_denied(test_framework):
        """Test that patients cannot hide/delete objects"""
        # Try to hide a visit
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # First create a visit to try to delete
        new_visit = {
            "establishment_id": "e1234567-89ab-cdef-0123-456789abcdef",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "visit_date": date.today().isoformat(),
            "diagnostic": f"Patient Delete Test {timestamp}",
            "treatment": f"Test Treatment {timestamp}",
            "summary": f"Visit for patient deletion test {timestamp}",
            "notes": "Test notes"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/{
                test_framework.john_doe_insurance}/visits",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_visit
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create visit for patient deletion test: {
                                 response.status_code}, {response.text}")

        visit_id = response.json()["visit_id"]

        # Now try to hide it as patient
        response = requests.delete(
            f"http://localhost:{test_framework.api_port}/api/visits/{visit_id}",
            headers={"Authorization": f"Bearer {test_framework.patient_token}"}
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied deleting visit with 403, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_hide_history_as_healthcare_professional(test_framework):
        """Test that healthcare professionals can hide medical history"""
        # Create a history record
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_history = {
            "diagnostic": f"Healthcare Delete Test {timestamp}",
            "treatment": f"Healthcare Test Treatment {timestamp}",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": date.today().isoformat(),
            "end_date": None
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/{
                test_framework.john_doe_insurance}/history",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_history
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create history for healthcare professional deletion test: {
                                 response.status_code}, {response.text}")

        history_id = response.json()["history_id"]

        # Now delete it as healthcare professional
        response = requests.delete(
            f"http://localhost:{test_framework.api_port}/api/history/{history_id}",
            headers={"Authorization": f"Bearer {
                test_framework.healthcare_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Healthcare professional failed to hide history: {
                                 response.status_code}, {response.text}")

    @suite.teardown
    def teardown_deletion_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

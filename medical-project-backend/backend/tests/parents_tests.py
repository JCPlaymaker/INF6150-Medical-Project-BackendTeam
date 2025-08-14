import requests
from datetime import datetime


def register_tests(suite, test_framework):
    """Register parent relationship tests with the provided test suite"""

    @suite.setup
    def setup_parents_tests(test_framework):
        """Setup tokens for testing parent relationship endpoints"""
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

            # Store known user IDs
            test_framework.john_doe_id = "99febb18-8a4c-40b6-942f-df3c60d522dd"  # parent
            test_framework.jane_smith_id = "ddb5502d-9c7c-46ed-9a5d-a27a32d29fa3"  # another parent
            test_framework.alfred_smith_id = "adbb8d39-0420-437e-8afa-63086fc54141"
            test_framework.hugh_mongus_id = "d10a3ded-3457-413e-8a5e-54f416667a11"

        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_add_parent_as_admin(test_framework):
        """Test adding a parent relationship as an admin"""
        # Create the parent-child relationship
        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.alfred_smith_id}/parents/{test_framework.john_doe_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to add parent relationship as admin: {
                                 response.status_code}, {response.text}")

        # Verify the relationship was added by checking child's data
        response = requests.get(
            # Hank's insurance ID
            f"http://localhost:{test_framework.api_port}/api/patients/INS111222",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get child data: {
                                 response.status_code}, {response.text}")

        child_data = response.json()
        parent_ids = [parent["parent"]["user_id"]
                      for parent in child_data.get("parents", [])]

        if test_framework.john_doe_id not in parent_ids:
            raise AssertionError(
                f"Added parent relationship not found in child data")

    @suite.test
    def test_add_parent_as_doctor(test_framework):
        """Test adding a parent relationship as a doctor"""
        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.alfred_smith_id}/parents/{test_framework.jane_smith_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"}
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to add parent relationship as doctor: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_add_parent_as_healthcare_professional(test_framework):
        """Test adding a parent relationship as a healthcare professional"""
        # First create a patient to use as parent (via admin)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
        new_patient = {
            "login": f"parentuser{timestamp}",
            "password": "testpassword",
            "user_type": "PATIENT",
            "first_name": "Parent",
            "last_name": "User",
            "phone_number": "555-123-4567",
            "email": f"parentuser{timestamp}@example.com",
            "medical_insurance_id": f"PINS{timestamp}",
            "gender": "Female",
            "city_of_birth": "Parent City",
            "date_of_birth": "1970-01-01",
            "coordinates": [
                {
                    "street_address": "123 Parent St",
                    "postal_code": "12345",
                    "city": "Parent City",
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
            raise AssertionError(f"Failed to create test parent: {
                                 response.status_code}, {response.text}")

        parent_id = response.json()["user_id"]

        # Now add the parent relationship as healthcare professional
        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.alfred_smith_id}/parents/{parent_id}",
            headers={"Authorization": f"Bearer {
                test_framework.healthcare_token}"}
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to add parent relationship as healthcare professional: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_add_parent_as_patient_denied(test_framework):
        """Test that a patient cannot add parent relationships"""
        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.alfred_smith_id}/parents/{test_framework.john_doe_id}",
            headers={"Authorization": f"Bearer {test_framework.patient_token}"}
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied with 403, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_hide_parent_relationship(test_framework):
        """Test hiding (deleting) a parent relationship"""
        # First add a parent relationship
        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.hugh_mongus_id}/parents/{test_framework.john_doe_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create parent relationship for hide test: {
                                 response.status_code}, {response.text}")

        # Now hide it
        response = requests.delete(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.hugh_mongus_id}/parents/{test_framework.john_doe_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to hide parent relationship: {
                                 response.status_code}, {response.text}")

        # Verify it's hidden by checking child data
        response = requests.get(
            # Hank's insurance ID
            f"http://localhost:{test_framework.api_port}/api/patients/INS222333",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get child data after hide: {
                                 response.status_code}, {response.text}")

        child_data = response.json()
        parent_ids = [parent["parent"]["user_id"]
                      for parent in child_data.get("parents", [])]

        if test_framework.john_doe_id in parent_ids:
            raise AssertionError(
                f"Hidden parent relationship still appears in child data")

    @suite.test
    def test_hide_parent_as_doctor(test_framework):
        """Test that a doctor can hide parent relationships"""
        # First add a parent relationship
        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.hugh_mongus_id}/parents/{test_framework.jane_smith_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create parent relationship for doctor-hide test: {
                                 response.status_code}, {response.text}")

        # Now hide it as doctor
        response = requests.delete(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.hugh_mongus_id}/parents/{test_framework.jane_smith_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Doctor failed to hide parent relationship: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_hide_parent_as_patient_denied(test_framework):
        """Test that a patient cannot hide parent relationships"""
        # First add a parent relationship
        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.hugh_mongus_id}/parents/{test_framework.alfred_smith_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create parent relationship for patient-hide test: {
                                 response.status_code}, {response.text}")

        # Now try to hide it as patient
        response = requests.delete(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.hugh_mongus_id}/parents/{test_framework.alfred_smith_id}",
            headers={"Authorization": f"Bearer {test_framework.patient_token}"}
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied with 403, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_add_parent_alt_as_admin(test_framework):
        """Test creating a new parent user and establishing relationship as an admin"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_parent_data = {
            "first_name": f"Parent{timestamp}",
            "last_name": "Creator",
            "phone_number": "555-123-4567",
            "email": f"parent{timestamp}@example.com",
            "gender": "Female"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.alfred_smith_id}/parents",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_parent_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create parent user with relationship: {
                response.status_code}, {response.text}")

        # Verify response contains the created user's ID
        data = response.json()
        if "user_id" not in data:
            raise AssertionError(f"Response does not contain user_id: {data}")

        # Store created parent ID for later tests
        test_framework.created_parent_id = data["user_id"]

        # Verify relationship was established by checking child's data
        response = requests.get(
            # Alfred Smith's insurance ID
            f"http://localhost:{test_framework.api_port}/api/patients/INS111222",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get child data: {
                response.status_code}, {response.text}")

        child_data = response.json()
        parent_ids = [parent["parent"]["user_id"]
                      for parent in child_data.get("parents", [])]

        if test_framework.created_parent_id not in parent_ids:
            raise AssertionError(
                f"Created parent relationship not found in child data")

    @suite.test
    def test_add_parent_alt_as_doctor(test_framework):
        """Test creating a new parent user and establishing relationship as a doctor"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_parent_data = {
            "first_name": f"DoctorCreated{timestamp}",
            "last_name": "Parent",
            "phone_number": "555-987-6543",
            "email": f"doctorcreated{timestamp}@example.com",
            "gender": "Male"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.hugh_mongus_id}/parents",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_parent_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create parent user with relationship as doctor: {
                response.status_code}, {response.text}")

    @suite.test
    def test_add_parent_alt_as_healthcare_professional(test_framework):
        """Test creating a new parent user and relationship as a healthcare professional"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_parent_data = {
            "first_name": f"HealthcareCreated{timestamp}",
            "last_name": "Parent",
            "phone_number": "555-111-2222",
            "email": f"healthcarecreated{timestamp}@example.com"
            # Test with missing optional gender field
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.alfred_smith_id}/parents",
            headers={"Authorization": f"Bearer {
                test_framework.healthcare_token}"},
            json=new_parent_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create parent user with relationship as healthcare professional: {
                response.status_code}, {response.text}")

    @suite.test
    def test_add_parent_alt_as_patient_denied(test_framework):
        """Test that a patient cannot create a new parent user with relationship"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_parent_data = {
            "first_name": f"PatientCreated{timestamp}",
            "last_name": "Parent",
            "phone_number": "555-333-4444",
            "email": f"patientcreated{timestamp}@example.com",
            "gender": "Female"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.alfred_smith_id}/parents",
            headers={"Authorization": f"Bearer {
                test_framework.patient_token}"},
            json=new_parent_data
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied with 403, but got {
                response.status_code}: {response.text}")

    @suite.test
    def test_add_parent_alt_validation_error(test_framework):
        """Test validation errors when creating a new parent user"""
        # Missing required fields
        invalid_parent = {
            "first_name": "Invalid",
            # Missing last_name
            "phone_number": "555-777-8888",
            # Missing email
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.alfred_smith_id}/parents",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=invalid_parent
        )

        # Should get 400 Bad Request
        if response.status_code != 400:
            raise AssertionError(f"Expected validation error with 400, but got {
                response.status_code}: {response.text}")

    @suite.test
    def test_add_parent_alt_nonexistent_child(test_framework):
        """Test creating a parent user for a non-existent child"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_parent_data = {
            "first_name": f"Orphan{timestamp}",
            "last_name": "Parent",
            "phone_number": "555-444-5555",
            "email": f"orphanparent{timestamp}@example.com",
            "gender": "Male"
        }

        # Use a non-existent UUID
        nonexistent_child_id = "00000000-0000-0000-0000-000000000000"

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                nonexistent_child_id}/parents",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_parent_data
        )

        # Should get 400 Bad Request or 404 Not Found (depends on implementation)
        if response.status_code not in [400, 404, 500]:
            raise AssertionError(f"Expected error response for non-existent child, but got {
                response.status_code}: {response.text}")

    @suite.teardown
    def teardown_parents_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

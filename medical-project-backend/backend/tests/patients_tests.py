import requests
from datetime import date, datetime


def register_tests(suite, test_framework):
    """Register patient-related tests with the provided test suite"""

    @suite.setup
    def setup_patients_tests(test_framework):
        """Setup tokens for testing patient endpoints"""
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

            # Get another patient token for testing access control
            patient2_token = test_framework.login_and_get_token(
                email="jane.smith@example.com",
                password="password2"
            )
            test_framework.patient2_token = patient2_token
        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_create_patient_as_admin(test_framework):
        """Test creating a new patient as an admin"""
        # Create a unique identifier for the test
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        # Create a patient
        new_patient = {
            "login": f"testpatient{unique_id}",
            "password": "testpassword",
            "user_type": "PATIENT",
            "first_name": "Test",
            "last_name": "Patient",
            "phone_number": "555-123-4567",
            "email": f"testpatient{unique_id}@example.com",
            "medical_insurance_id": f"INS{unique_id}",
            "gender": "Other",
            "city_of_birth": "Test City",
            "date_of_birth": "2000-01-01",
            "coordinates": [
                {
                    "street_address": "123 Test St",
                    "apartment": "Apt 1",
                    "postal_code": "12345",
                    "city": "Test City",
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
            raise AssertionError(f"Failed to create patient as admin: {
                                 response.status_code}, {response.text}")

        # Verify response contains the created patient's user_id
        data = response.json()
        if "user_id" not in data:
            raise AssertionError(f"Response does not contain user_id: {data}")

        # Store created patient ID for later tests
        test_framework.created_patient_user_id = data["user_id"]
        test_framework.created_patient_insurance_id = f"INS{unique_id}"

    @suite.test
    def test_create_patient_as_doctor(test_framework):
        """Test creating a new patient as a doctor"""
        # Create a unique identifier for the test
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        new_patient = {
            "login": f"doctorpatient{unique_id}",
            "password": "testpassword",
            "user_type": "PATIENT",
            "first_name": "Doctor",
            "last_name": "Created",
            "phone_number": "555-987-6543",
            "email": f"doctorcreated{unique_id}@example.com",
            "medical_insurance_id": f"DINS{unique_id}",
            "gender": "Female",
            "city_of_birth": "Doctor City",
            "date_of_birth": "1995-05-05",
            "coordinates": [
                {
                    "street_address": "456 Doctor Ave",
                    "apartment": "Suite 2",
                    "postal_code": "54321",
                    "city": "Doctor City",
                    "country": "Test Country"
                }
            ]
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_patient
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create patient as doctor: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_create_patient_as_patient_denied(test_framework):
        """Test that patients cannot create other patients"""
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        new_patient = {
            "login": f"patientcreated{unique_id}",
            "password": "testpassword",
            "user_type": "PATIENT",
            "first_name": "Patient",
            "last_name": "Created",
            "phone_number": "555-111-2222",
            "email": f"patientcreated{unique_id}@example.com",
            "medical_insurance_id": f"PINS{unique_id}",
            "gender": "Male",
            "city_of_birth": "Patient City",
            "date_of_birth": "1990-10-10",
            "coordinates": [
                {
                    "street_address": "789 Patient St",
                    "postal_code": "98765",
                    "city": "Patient City",
                    "country": "Test Country"
                }
            ]
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients",
            headers={"Authorization": f"Bearer {
                test_framework.patient_token}"},
            json=new_patient
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied with 403, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_create_patient_with_parent_relationship(test_framework):
        """Test creating a patient with parent relationships"""
        # First, ensure we have a parent ID available
        parent_id = "99febb18-8a4c-40b6-942f-df3c60d522dd"  # From test data

        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        new_patient = {
            "login": f"childpatient{unique_id}",
            "password": "testpassword",
            "user_type": "PATIENT",
            "first_name": "Child",
            "last_name": "Patient",
            "phone_number": "555-333-4444",
            "email": f"childpatient{unique_id}@example.com",
            "medical_insurance_id": f"CINS{unique_id}",
            "gender": "Female",
            "city_of_birth": "Child City",
            "date_of_birth": "2010-12-12",
            "coordinates": [
                {
                    "street_address": "101 Child St",
                    "postal_code": "11111",
                    "city": "Child City",
                    "country": "Test Country"
                }
            ],
            "parent_ids": [parent_id]
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_patient
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create patient with parent relationship: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_get_patient_details(test_framework):
        """Test retrieving patient details"""
        # We'll use an existing patient ID from test data
        patient_id = "INS123456"

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/{patient_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get patient details: {
                                 response.status_code}, {response.text}")

        # Verify that the response contains the expected data
        data = response.json()
        if data.get("medical_insurance_id") != patient_id:
            raise AssertionError(f"Expected medical_insurance_id to be {
                                 patient_id}, got {data.get('medical_insurance_id')}")

        # Check that all expected sections are present
        required_sections = ["coordinates",
                             "medical_history", "medical_visits", "parents"]
        for section in required_sections:
            if section not in data:
                raise AssertionError(
                    f"Response is missing required section '{section}'")

    @suite.test
    def test_patient_self_access(test_framework):
        """Test that a patient can access their own details"""
        patient_id = "INS123456"  # This should match the patient's ID that has patient_token

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/{patient_id}",
            headers={"Authorization": f"Bearer {test_framework.patient_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Patient could not access their own details: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_patient_cannot_access_other_patient(test_framework):
        """Test that a patient cannot access another patient's details"""
        other_patient_id = "INS654321"  # ID of a different patient

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/{other_patient_id}",
            headers={"Authorization": f"Bearer {test_framework.patient_token}"}
        )

        # Should be denied
        if response.status_code != 403:
            raise AssertionError(f"Expected 403 Forbidden when patient tries to access another patient's data, got {
                                 response.status_code}")

    @suite.test
    def test_doctor_can_access_patient(test_framework):
        """Test that a doctor can access any patient's details"""
        patient_id = "INS123456"

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/{patient_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Doctor could not access patient details: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_update_patient(test_framework):
        """Test updating a patient's information"""
        # First create a patient to update
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        new_patient = {
            "login": f"updatepatient{unique_id}",
            "password": "testpassword",
            "user_type": "PATIENT",
            "first_name": "Update",
            "last_name": "Patient",
            "phone_number": "555-555-5555",
            "email": f"updatepatient{unique_id}@example.com",
            "medical_insurance_id": f"UINS{unique_id}",
            "gender": "Male",
            "city_of_birth": "Update City",
            "date_of_birth": "1985-01-01",
            "coordinates": [
                {
                    "street_address": "222 Update St",
                    "postal_code": "22222",
                    "city": "Update City",
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
            raise AssertionError(f"Failed to create patient for update test: {
                                 response.status_code}, {response.text}")

        medical_insurance_id = f"UINS{unique_id}"

        # Now update the patient
        update_data = {
            "login": f"updatedpatient{unique_id}",
            "gender": "Female",
            "city_of_birth": "Updated City",
            "date_of_birth": "1985-01-01",
            "first_name": "Updated",
            "last_name": "Patient",
            "phone_number": "555-666-7777",
            "email": f"updatedpatient{unique_id}@example.com"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/patients/{
                medical_insurance_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=update_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to update patient: {
                                 response.status_code}, {response.text}")

        # Verify updated data in response
        data = response.json()
        if data.get("first_name") != "Updated":
            raise AssertionError(
                f"Updated first_name not reflected in response: {data}")

    @suite.test
    def test_update_patient_as_doctor(test_framework):
        """Test that a doctor can update a patient's information"""
        # Use a patient created in previous tests
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        new_patient = {
            "login": f"doctorupdatepatient{unique_id}",
            "password": "testpassword",
            "user_type": "PATIENT",
            "first_name": "Doctor",
            "last_name": "Update",
            "phone_number": "555-888-9999",
            "email": f"doctorupdatepatient{unique_id}@example.com",
            "medical_insurance_id": f"DUINS{unique_id}",
            "gender": "Male",
            "city_of_birth": "Doctor City",
            "date_of_birth": "1975-05-05",
            "coordinates": [
                {
                    "street_address": "333 Doctor St",
                    "postal_code": "33333",
                    "city": "Doctor City",
                    "country": "Test Country"
                }
            ]
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_patient
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create patient for doctor update test: {
                                 response.status_code}, {response.text}")

        medical_insurance_id = f"DUINS{unique_id}"

        update_data = {
            "login": f"doctorUpdatedPatient{unique_id}",
            "gender": "Female",
            "city_of_birth": "Doctor Updated City",
            "date_of_birth": "1975-05-05",
            "first_name": "Doctor",
            "last_name": "Updated",
            "phone_number": "555-000-1111",
            "email": f"doctorupdatedpatient{unique_id}@example.com"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/patients/{
                medical_insurance_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=update_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Doctor failed to update patient: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_update_patient_as_patient_denied(test_framework):
        """Test that a patient cannot update another patient's information"""
        # Use a known patient ID that is not the authenticated patient
        other_patient_id = "INS654321"

        update_data = {
            "login": "shouldnotupdate",
            "gender": "Other",
            "city_of_birth": "Denied City",
            "first_name": "Should",
            "last_name": "Deny",
            "phone_number": "555-999-8888",
            "email": "shoulddeny@example.com"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/patients/{other_patient_id}",
            headers={"Authorization": f"Bearer {
                test_framework.patient_token}"},
            json=update_data
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied with 403 when updating another patient, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_create_patient_validation_error(test_framework):
        """Test validation errors when creating a patient"""
        # Missing required fields
        invalid_patient = {
            "login": "invalidpatient",
            "password": "testpassword",
            # Missing user_type, first_name, etc.
            "email": "invalidpatient@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=invalid_patient
        )

        # Should get 400 Bad Request
        if response.status_code != 400:
            raise AssertionError(f"Expected validation error with 400, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_get_nonexistent_patient(test_framework):
        """Test getting a non-existent patient"""
        nonexistent_id = "NONEXISTENT123"  # Non-existent ID

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/{nonexistent_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        # Should get 404 Not Found
        if response.status_code != 404:
            raise AssertionError(f"Expected 404 Not Found for non-existent patient, but got {
                                 response.status_code}: {response.text}")

    @suite.teardown
    def teardown_patients_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

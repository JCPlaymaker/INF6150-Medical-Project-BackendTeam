import requests
from datetime import datetime


def register_tests(suite, test_framework):
    """Register coordinate route tests with the provided test suite"""

    @suite.setup
    def setup_coordinate_tests(test_framework):
        """Setup tokens for testing coordinate endpoints"""
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

            # Get patient token for John Doe (who has INS123456)
            patient_token = test_framework.login_and_get_token(
                email="john.doe@example.com",
                password="password1"
            )
            test_framework.patient_token = patient_token

            # Get patient token for Jane Smith (who has INS654321)
            patient2_token = test_framework.login_and_get_token(
                email="jane.smith@example.com",
                password="password2"
            )
            test_framework.patient2_token = patient2_token

            # Store known user IDs
            test_framework.john_doe_id = "99febb18-8a4c-40b6-942f-df3c60d522dd"
            test_framework.jane_smith_id = "ddb5502d-9c7c-46ed-9a5d-a27a32d29fa3"

        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_add_coordinate_as_admin(test_framework):
        """Test adding a coordinate as an admin user"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        coordinate_data = {
            "street_address": f"123 Admin St {timestamp}",
            "apartment": "Suite 100",
            "postal_code": "12345",
            "city": "Admin City",
            "country": "Test Country"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.john_doe_id}/coordinates",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=coordinate_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to add coordinate as admin: {
                                 response.status_code}, {response.text}")

        # Check response contains coordinate_id
        data = response.json()
        if "coordinate_id" not in data:
            raise AssertionError(
                f"Response does not contain coordinate_id: {data}")

        # Store for future tests
        test_framework.created_coordinate_id = data["coordinate_id"]

    @suite.test
    def test_add_coordinate_as_doctor(test_framework):
        """Test adding a coordinate as a doctor"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        coordinate_data = {
            "street_address": f"456 Doctor St {timestamp}",
            "apartment": "Floor 2",
            "postal_code": "54321",
            "city": "Doctor City",
            "country": "Test Country"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.john_doe_id}/coordinates",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=coordinate_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to add coordinate as doctor: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_add_coordinate_as_self(test_framework):
        """Test adding a coordinate as the user themselves"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        coordinate_data = {
            "street_address": f"789 Self St {timestamp}",
            "apartment": "Apt 3B",
            "postal_code": "98765",
            "city": "Self City",
            "country": "Test Country"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.john_doe_id}/coordinates",
            headers={"Authorization": f"Bearer {
                test_framework.patient_token}"},
            json=coordinate_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to add coordinate as self: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_add_coordinate_as_another_patient_denied(test_framework):
        """Test that a patient cannot add coordinates for another patient"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        coordinate_data = {
            "street_address": f"111 Other St {timestamp}",
            "postal_code": "11111",
            "city": "Other City",
            "country": "Test Country"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.jane_smith_id}/coordinates",
            headers={"Authorization": f"Bearer {
                test_framework.patient_token}"},
            json=coordinate_data
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied with 403, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_update_coordinate(test_framework):
        """Test updating a coordinate"""
        # First need to add a coordinate to update
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        coordinate_data = {
            "street_address": f"222 Update St {timestamp}",
            "postal_code": "22222",
            "city": "Update City",
            "country": "Test Country"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.john_doe_id}/coordinates",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=coordinate_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create coordinate for update test: {
                                 response.status_code}, {response.text}")

        coordinate_id = response.json()["coordinate_id"]

        # Now update the coordinate
        update_data = {
            "street_address": f"222 Updated St {timestamp}",
            "apartment": "Updated Apt",
            "postal_code": "33333",
            "city": "Updated City",
            "country": "Updated Country"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/coordinates/{coordinate_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=update_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to update coordinate: {
                                 response.status_code}, {response.text}")

        # Verify the updated data
        data = response.json()
        if data.get("street_address") != update_data["street_address"]:
            raise AssertionError(
                f"Updated street_address not reflected in response: {data}")
        if data.get("city") != update_data["city"]:
            raise AssertionError(
                f"Updated city not reflected in response: {data}")

    @suite.test
    def test_update_coordinate_as_doctor(test_framework):
        """Test that a doctor can update coordinates"""
        # Use a coordinate created in a previous test
        if not hasattr(test_framework, "created_coordinate_id"):
            raise AssertionError("No coordinate ID available for test")

        coordinate_id = test_framework.created_coordinate_id
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        update_data = {
            "street_address": f"Doctor Updated St {timestamp}",
            "apartment": "Dr. Office",
            "postal_code": "44444",
            "city": "Doctor City",
            "country": "Doctor Country"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/coordinates/{coordinate_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=update_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Doctor failed to update coordinate: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_update_coordinate_as_self(test_framework):
        """Test that a user can update their own coordinates"""
        # First add a coordinate for the patient
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        coordinate_data = {
            "street_address": f"Self St {timestamp}",
            "postal_code": "55555",
            "city": "Self City",
            "country": "Self Country"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.john_doe_id}/coordinates",
            headers={"Authorization": f"Bearer {
                test_framework.patient_token}"},
            json=coordinate_data
        )

        if response.status_code != 201:
            raise AssertionError(
                f"Failed to create coordinate for self-update test: {response.status_code}, {response.text}")

        coordinate_id = response.json()["coordinate_id"]

        # Now update it
        update_data = {
            "street_address": f"Self Updated St {timestamp}",
            "apartment": "My Apt",
            "postal_code": "66666",
            "city": "My City",
            "country": "My Country"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/coordinates/{coordinate_id}",
            headers={"Authorization": f"Bearer {
                test_framework.patient_token}"},
            json=update_data
        )

        if response.status_code != 201:
            raise AssertionError(
                f"Self-update of coordinate failed: {response.status_code}, {response.text}")

    @suite.test
    def test_hide_coordinate(test_framework):
        """Test hiding (deleting) a coordinate"""
        # First add a coordinate to hide
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        coordinate_data = {
            "street_address": f"Delete St {timestamp}",
            "postal_code": "77777",
            "city": "Delete City",
            "country": "Delete Country"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.john_doe_id}/coordinates",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=coordinate_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create coordinate for hide test: {
                                 response.status_code}, {response.text}")

        coordinate_id = response.json()["coordinate_id"]

        # Now hide it
        response = requests.delete(
            f"http://localhost:{test_framework.api_port}/api/coordinates/{coordinate_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to hide coordinate: {
                                 response.status_code}, {response.text}")

        # Verify it's hidden by checking patient data
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get patient data after hide: {
                                 response.status_code}, {response.text}")

        patient_data = response.json()
        coordinate_ids = [coord["id"] for coord in patient_data["coordinates"]]

        if coordinate_id in coordinate_ids:
            raise AssertionError(f"Hidden coordinate {
                                 coordinate_id} still appears in patient data")

    @suite.test
    def test_hide_coordinate_as_patient_denied(test_framework):
        """Test that a patient cannot hide coordinates"""
        # First add a coordinate using admin
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        coordinate_data = {
            "street_address": f"Patient Delete St {timestamp}",
            "postal_code": "88888",
            "city": "Patient Delete City",
            "country": "Patient Delete Country"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.john_doe_id}/coordinates",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=coordinate_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create coordinate for patient-hide test: {
                                 response.status_code}, {response.text}")

        coordinate_id = response.json()["coordinate_id"]

        # Now try to hide it as patient
        response = requests.delete(
            f"http://localhost:{test_framework.api_port}/api/coordinates/{coordinate_id}",
            headers={"Authorization": f"Bearer {test_framework.patient_token}"}
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied with 403, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_coordinate_validation_error(test_framework):
        """Test validation errors when creating a coordinate"""
        # Missing required fields
        invalid_coordinate = {
            "street_address": "123 Invalid St",
            # Missing postal_code and city
            "country": "Test Country"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.john_doe_id}/coordinates",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=invalid_coordinate
        )

        # Should get 400 Bad Request
        if response.status_code != 400:
            raise AssertionError(f"Expected validation error with 400, but got {
                                 response.status_code}: {response.text}")

    @suite.teardown
    def teardown_coordinate_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

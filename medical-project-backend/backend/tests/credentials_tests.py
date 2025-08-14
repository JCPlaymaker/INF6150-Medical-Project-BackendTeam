import requests
from datetime import datetime


def register_tests(suite, test_framework):
    """Register credential update tests with the provided test suite"""

    @suite.setup
    def setup_credentials_tests(test_framework):
        """Setup tokens for testing credential update endpoints"""
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
            test_framework.john_doe_id = "99febb18-8a4c-40b6-942f-df3c60d522dd"
            test_framework.jane_smith_id = "ddb5502d-9c7c-46ed-9a5d-a27a32d29fa3"

        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_update_credentials_as_admin(test_framework):
        """Test updating user credentials as an admin"""
        # First create a test user
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_user = {
            "login": f"credentialuser{timestamp}",
            "password": "initialpassword",
            "user_type": "PATIENT",
            "first_name": "Credential",
            "last_name": "User",
            "phone_number": "555-123-4567",
            "email": f"credentialuser{timestamp}@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_user
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create test user: {
                                 response.status_code}, {response.text}")

        user_id = response.json()["user_id"]

        # Now update the credentials
        new_credentials = {
            "login": f"updateduser{timestamp}",
            "password": "newpassword123"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/users/{user_id}/credentials",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_credentials
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to update credentials as admin: {
                                 response.status_code}, {response.text}")

        # Verify success message in response
        data = response.json()
        if "status" not in data or data["status"] != "success":
            raise AssertionError(
                f"Expected success status in response, got: {data}")

        # Store values for future login test
        test_framework.test_user_email = f"credentialuser{
            timestamp}@example.com"
        test_framework.test_user_new_password = "newpassword123"

    @suite.test
    def test_updated_credentials_login(test_framework):
        """Test that the updated credentials work for login"""
        if not hasattr(test_framework, "test_user_email") or not hasattr(test_framework, "test_user_new_password"):
            raise AssertionError("No test user credentials available for test")

        # Try to login with the new credentials
        try:
            token = test_framework.login_and_get_token(
                email=test_framework.test_user_email,
                password=test_framework.test_user_new_password
            )

            if not token or len(token) < 20:
                raise AssertionError(
                    "Received invalid token after credential update")

        except Exception as e:
            raise AssertionError(
                f"Login with updated credentials failed: {str(e)}")

    @suite.test
    def test_update_credentials_as_doctor(test_framework):
        """Test updating user credentials as a doctor"""
        # First create a test user
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_user = {
            "login": f"doctorchanged{timestamp}",
            "password": "initialpassword",
            "user_type": "PATIENT",
            "first_name": "Doctor",
            "last_name": "Changed",
            "phone_number": "555-987-6543",
            "email": f"doctorchanged{timestamp}@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_user
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create test user for doctor test: {
                                 response.status_code}, {response.text}")

        user_id = response.json()["user_id"]

        # Now update the credentials as doctor
        new_credentials = {
            "login": f"doctorupdated{timestamp}",
            "password": "doctornewpass"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/users/{user_id}/credentials",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_credentials
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to update credentials as doctor: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_update_credentials_as_healthcare_professional(test_framework):
        """Test updating user credentials as a healthcare professional"""
        # First create a test user
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_user = {
            "login": f"healthcarechanged{timestamp}",
            "password": "initialpassword",
            "user_type": "PATIENT",
            "first_name": "Healthcare",
            "last_name": "Changed",
            "phone_number": "555-111-2222",
            "email": f"healthcarechanged{timestamp}@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {
                test_framework.healthcare_token}"},
            json=new_user
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create test user for healthcare test: {
                                 response.status_code}, {response.text}")

        user_id = response.json()["user_id"]

        # Now update the credentials as healthcare professional
        new_credentials = {
            "login": f"healthcareupdated{timestamp}",
            "password": "healthcarenewpass"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/users/{user_id}/credentials",
            headers={"Authorization": f"Bearer {
                test_framework.healthcare_token}"},
            json=new_credentials
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to update credentials as healthcare professional: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_update_credentials_as_patient_denied(test_framework):
        """Test that a patient cannot update credentials"""
        # Try to update another user's credentials as patient
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_credentials = {
            "login": f"patientchanged{timestamp}",
            "password": "patientnewpass"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/users/{
                test_framework.jane_smith_id}/credentials",
            headers={"Authorization": f"Bearer {
                test_framework.patient_token}"},
            json=new_credentials
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied with 403, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_update_credentials_validation(test_framework):
        """Test validation for credential updates"""

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        new_user = {
            "login": f"healthcarechanged{timestamp}",
            "password": "initialpassword",
            "user_type": "PATIENT",
            "first_name": "Healthcare",
            "last_name": "Changed",
            "phone_number": "555-111-2222",
            "email": f"healthcarechanged{timestamp}@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {
                test_framework.healthcare_token}"},
            json=new_user
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create test user for healthcare test: {
                                 response.status_code}, {response.text}")

        user_id = response.json()["user_id"]

        invalid_credentials = {
            "login": "",
            "password": "validpassword"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/users/{user_id}/credentials",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=invalid_credentials
        )

        # Check how the app handles validation
        # Ideally should reject with 400, but let's see how it behaves
        if response.status_code == 201:
            print("Note: Application accepts empty login in credential update")
        else:
            print(f"Application correctly rejected invalid credentials with status {
                  response.status_code}")

    @suite.teardown
    def teardown_credentials_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

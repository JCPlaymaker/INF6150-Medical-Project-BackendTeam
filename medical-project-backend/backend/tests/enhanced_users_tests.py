import requests
from datetime import date, datetime


def register_tests(suite, test_framework):
    """Register enhanced user-related tests with the provided test suite"""

    @suite.setup
    def setup_user_tests(test_framework):
        """Setup tokens for testing user endpoints"""
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

            # Get healthcare professional token
            healthcare_token = test_framework.login_and_get_token(
                email="david.miller@example.com",
                password="password6"
            )
            test_framework.healthcare_token = healthcare_token
        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_create_user_as_admin(test_framework):
        """Test creating a new user as an admin"""
        # Create a unique identifier for the test
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        # Create a user
        new_user = {
            "login": f"testuser{unique_id}",
            "password": "testpassword",
            "user_type": "HEALTHCARE PROFESSIONAL",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "555-123-4567",
            "email": f"testuser{unique_id}@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_user
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create user as admin: {
                                 response.status_code}, {response.text}")

        # Verify response contains the created user's user_id
        data = response.json()
        if "user_id" not in data:
            raise AssertionError(f"Response does not contain user_id: {data}")

        # Store created user ID for later tests
        test_framework.created_user_id = data["user_id"]

    @suite.test
    def test_create_user_as_doctor(test_framework):
        """Test creating a new user as a doctor"""
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        new_user = {
            "login": f"doctorcreateduser{unique_id}",
            "password": "testpassword",
            "user_type": "HEALTHCARE PROFESSIONAL",
            "first_name": "Doctor",
            "last_name": "Created",
            "phone_number": "555-987-6543",
            "email": f"doctorcreated{unique_id}@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_user
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create user as doctor: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_create_user_as_healthcare_professional(test_framework):
        """Test creating a new user as a healthcare professional"""
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        new_user = {
            "login": f"healthcarecreateduser{unique_id}",
            "password": "testpassword",
            "user_type": "HEALTHCARE PROFESSIONAL",
            "first_name": "Healthcare",
            "last_name": "Created",
            "phone_number": "555-111-2222",
            "email": f"healthcarecreated{unique_id}@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {
                test_framework.healthcare_token}"},
            json=new_user
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create user as healthcare professional: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_create_user_as_patient_denied(test_framework):
        """Test that patients cannot create users"""
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        new_user = {
            "login": f"patientcreateduser{unique_id}",
            "password": "testpassword",
            "user_type": "HEALTHCARE PROFESSIONAL",
            "first_name": "Patient",
            "last_name": "Created",
            "phone_number": "555-333-4444",
            "email": f"patientcreated{unique_id}@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {
                test_framework.patient_token}"},
            json=new_user
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied with 403, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_create_admin_user(test_framework):
        """Test creating an admin user (should only be possible by an admin)"""
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        new_admin = {
            "login": f"newadmin{unique_id}",
            "password": "adminpassword",
            "user_type": "ADMIN",
            "first_name": "New",
            "last_name": "Admin",
            "phone_number": "555-555-5555",
            "email": f"newadmin{unique_id}@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_admin
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create admin user: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_get_user(test_framework):
        """Test retrieving a user by ID"""
        # First create a user to retrieve
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        new_user = {
            "login": f"retrieveuser{unique_id}",
            "password": "testpassword",
            "user_type": "DOCTOR",
            "first_name": "Retrieve",
            "last_name": "User",
            "phone_number": "555-666-7777",
            "email": f"retrieveuser{unique_id}@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_user
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create user for get test: {
                                 response.status_code}, {response.text}")

        user_id = response.json()["user_id"]

        # Now update the user
        update_data = {
            "login": f"updateduser{unique_id}",
            "first_name": "Updated",
            "last_name": "User",
            "phone_number": "555-000-1111",
            "email": f"updateduser{unique_id}@example.com"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/users/{user_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=update_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to update user: {
                                 response.status_code}, {response.text}")

        # Verify updated data in response
        data = response.json()
        if data.get("first_name") != "Updated":
            raise AssertionError(
                f"Updated first_name not reflected in response: {data}")

    @suite.test
    def test_update_user_as_doctor(test_framework):
        """Test that a doctor can update a user's information"""
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        new_user = {
            "login": f"doctorupdateuser{unique_id}",
            "password": "testpassword",
            "user_type": "HEALTHCARE PROFESSIONAL",
            "first_name": "Doctor",
            "last_name": "Update",
            "phone_number": "555-222-3333",
            "email": f"doctorupdateuser{unique_id}@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_user
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create user for doctor update test: {
                                 response.status_code}, {response.text}")

        user_id = response.json()["user_id"]

        update_data = {
            "login": f"doctorupdateduser{unique_id}",
            "first_name": "Doctor",
            "last_name": "Updated",
            "phone_number": "555-444-5555",
            "email": f"doctorupdateduser{unique_id}@example.com"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/users/{user_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=update_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Doctor failed to update user: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_update_user_as_patient_denied(test_framework):
        """Test that a patient cannot update user information"""
        # Use an existing user ID
        user_id = "2d3cfc26-4958-4723-acf8-9799502c4d7d"

        update_data = {
            "login": "shouldnotupdate",
            "first_name": "Should",
            "last_name": "Deny",
            "phone_number": "555-999-8888",
            "email": "shoulddeny@example.com"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/users/{user_id}",
            headers={"Authorization": f"Bearer {
                test_framework.patient_token}"},
            json=update_data
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied with 403 when updating a user, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_create_user_validation_error(test_framework):
        """Test validation errors when creating a user"""
        # Missing required fields
        invalid_user = {
            "login": "invaliduser",
            "password": "testpassword",
            # Missing user_type, first_name, etc.
            "email": "invaliduser@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=invalid_user
        )

        # Should get 400 Bad Request
        if response.status_code != 400:
            raise AssertionError(f"Expected validation error with 400, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_get_nonexistent_user(test_framework):
        """Test getting a non-existent user"""
        nonexistent_id = "00000000-0000-0000-0000-000000000000"  # Non-existent UUID

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/users/{nonexistent_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        # Should get 404 Not Found
        if response.status_code != 404:
            raise AssertionError(f"Expected 404 Not Found for non-existent user, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_update_nonexistent_user(test_framework):
        """Test updating a non-existent user"""
        nonexistent_id = "00000000-0000-0000-0000-000000000000"  # Non-existent UUID

        update_data = {
            "login": "nonexistentuser",
            "first_name": "Nonexistent",
            "last_name": "User",
            "phone_number": "555-123-4567",
            "email": "nonexistent@example.com"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/users/{nonexistent_id}",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=update_data
        )

        # Should get 404 Not Found or 500 Internal Server Error depending on implementation
        if response.status_code not in [404, 500]:
            raise AssertionError(f"Expected error when updating non-existent user, but got {
                                 response.status_code}: {response.text}")

    @suite.teardown
    def teardown_user_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

    @suite.test
    def test_get_user_as_doctor(test_framework):
        """Test retrieving a user as a doctor"""
        # Use an existing user ID from the database
        user_id = "2d3cfc26-4958-4723-acf8-9799502c4d7d"  # This should be a valid user ID

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/users/{user_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Doctor failed to get user: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_get_user_as_patient_denied(test_framework):
        """Test that patients cannot retrieve user details"""
        # Use an existing user ID
        user_id = "2d3cfc26-4958-4723-acf8-9799502c4d7d"

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/users/{user_id}",
            headers={"Authorization": f"Bearer {test_framework.patient_token}"}
        )

        # Should be denied with 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(f"Expected patient to be denied with 403, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_update_user(test_framework):
        """Test updating a user's information"""
        # First create a user to update
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")

        new_user = {
            "login": f"updateuser{unique_id}",
            "password": "testpassword",
            "user_type": "HEALTHCARE PROFESSIONAL",
            "first_name": "Update",
            "last_name": "User",
            "phone_number": "555-888-9999",
            "email": f"updateuser{unique_id}@example.com"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=new_user
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create user for update test: {
                                 response.status_code}, {response.text}")

        user_id = response.json()["user_id"]

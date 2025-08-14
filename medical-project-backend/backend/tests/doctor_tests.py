import requests


def register_tests(suite, test_framework):
    """Register doctor route tests with the provided test suite"""

    @suite.setup
    def setup_doctor_tests(test_framework):
        """Setup tokens for testing doctor endpoints"""
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

        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_get_doctors_as_admin(test_framework):
        """Test retrieving all doctors as an admin user"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/doctors",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get doctors as admin: {
                                 response.status_code}, {response.text}")

        data = response.json()

        # Verify response structure
        if "status" not in data or data["status"] != "success":
            raise AssertionError(f"Expected 'success' status, got: {
                                 data.get('status', 'missing')}")

        if "data" not in data or not isinstance(data["data"], list):
            raise AssertionError(
                "Expected 'data' field with a list of doctors")

        # Verify that we have at least one doctor
        if len(data["data"]) == 0:
            raise AssertionError(
                "Expected at least one doctor in the response")

        # Verify doctor data structure
        doctor = data["data"][0]
        required_fields = ["user_id", "first_name",
                           "last_name", "email", "phone_number"]

        for field in required_fields:
            if field not in doctor:
                raise AssertionError(f"Required field '{
                                     field}' missing from doctor data")

        # Verify that Alice Brown is in the response
        found_alice = False
        for doctor in data["data"]:
            if (doctor["first_name"] == "Alice" and doctor["last_name"] == "Brown" and
                    doctor["email"] == "alice.brown@example.com"):
                found_alice = True
                break

        if not found_alice:
            raise AssertionError(
                "Could not find test doctor 'Alice Brown' in the response")

    @suite.test
    def test_get_doctors_as_doctor(test_framework):
        """Test retrieving all doctors as a doctor user"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/doctors",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get doctors as doctor: {
                                 response.status_code}, {response.text}")

        # Verify we have data in the response
        data = response.json()
        if "data" not in data or not isinstance(data["data"], list) or len(data["data"]) == 0:
            raise AssertionError("Expected non-empty data array in response")

    @suite.test
    def test_get_doctors_as_healthcare_professional(test_framework):
        """Test retrieving all doctors as a healthcare professional"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/doctors",
            headers={"Authorization": f"Bearer {
                test_framework.healthcare_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get doctors as healthcare professional: {
                                 response.status_code}, {response.text}")

        # Verify we have data in the response
        data = response.json()
        if "data" not in data or not isinstance(data["data"], list) or len(data["data"]) == 0:
            raise AssertionError("Expected non-empty data array in response")

    @suite.test
    def test_get_doctors_without_token(test_framework):
        """Test that unauthorized access is properly rejected"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/doctors"
        )

        # Should get 401 Unauthorized
        if response.status_code != 401:
            raise AssertionError(f"Expected 401 Unauthorized for missing token, got {
                                 response.status_code}")

    @suite.test
    def test_get_doctors_with_invalid_token(test_framework):
        """Test that access with invalid token is properly rejected"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/doctors",
            headers={"Authorization": "Bearer invalid_token_here"}
        )

        # Should get 401 or 422 (token validation error)
        if response.status_code not in [401, 422]:
            raise AssertionError(
                f"Expected 401/422 for invalid token, got {response.status_code}")

    @suite.teardown
    def teardown_doctor_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

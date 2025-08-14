import requests


def register_tests(suite, test_framework):
    """Register establishment route tests with the provided test suite"""

    @suite.setup
    def setup_establishment_tests(test_framework):
        """Setup tokens for testing establishment endpoints"""
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

        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_get_establishments_as_admin(test_framework):
        """Test retrieving all establishments as an admin user"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/establishments",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get establishments as admin: {
                                 response.status_code}, {response.text}")

        data = response.json()

        # Verify response structure
        if "status" not in data or data["status"] != "success":
            raise AssertionError(f"Expected 'success' status, got: {
                                 data.get('status', 'missing')}")

        if "data" not in data or not isinstance(data["data"], list):
            raise AssertionError(
                "Expected 'data' field with a list of establishments")

        # Verify that we have at least one establishment
        if len(data["data"]) == 0:
            raise AssertionError(
                "Expected at least one establishment in the response")

        # Verify establishment data structure
        establishment = data["data"][0]
        required_fields = ["establishment_id",
                           "establishment_name", "created_at"]

        for field in required_fields:
            if field not in establishment:
                raise AssertionError(f"Required field '{
                                     field}' missing from establishment data")

        # Verify that Central City Hospital is in the response
        found_central_hospital = False
        for establishment in data["data"]:
            if establishment["establishment_name"] == "Central City Hospital":
                found_central_hospital = True
                break

        if not found_central_hospital:
            raise AssertionError(
                "Could not find test establishment 'Central City Hospital' in the response")

    @suite.test
    def test_get_establishments_as_doctor(test_framework):
        """Test retrieving all establishments as a doctor user"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/establishments",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get establishments as doctor: {
                                 response.status_code}, {response.text}")

        # Verify we have data in the response
        data = response.json()
        if "data" not in data or not isinstance(data["data"], list) or len(data["data"]) == 0:
            raise AssertionError("Expected non-empty data array in response")

    @suite.test
    def test_get_establishments_without_token(test_framework):
        """Test that unauthorized access is properly rejected"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/establishments"
        )

        # Should get 401 Unauthorized
        if response.status_code != 401:
            raise AssertionError(f"Expected 401 Unauthorized for missing token, got {
                                 response.status_code}")

    @suite.test
    def test_get_establishments_with_expired_token(test_framework):
        """Test that access with expired token is properly rejected"""
        # First login and logout to blacklist the token
        token = test_framework.login_and_get_token(
            email="john.doe@example.com",
            password="password1"
        )

        # Logout to blacklist the token
        logout_response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

        if logout_response.status_code != 200:
            raise AssertionError(
                f"Failed to logout/blacklist token: {logout_response.status_code}")

        # Now try to use the blacklisted token
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/establishments",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should get 401 Unauthorized
        if response.status_code != 401:
            raise AssertionError(f"Expected 401 for blacklisted token, got {
                                 response.status_code}")

    @suite.test
    def test_establishments_count(test_framework):
        """Test that the correct number of establishments is returned"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/establishments",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get establishments: {
                                 response.status_code}, {response.text}")

        data = response.json()

        # In the test data, there should be 3 establishments
        if len(data["data"]) != 3:
            raise AssertionError(f"Expected 3 establishments, got {
                                 len(data['data'])}")

        # Verify establishments from test data
        establishment_names = ["Central City Hospital",
                               "Westside Medical Center", "Eastgate Health Clinic"]
        found_establishments = [e["establishment_name"] for e in data["data"]]

        for name in establishment_names:
            if name not in found_establishments:
                raise AssertionError(f"Expected establishment '{
                                     name}' not found in response")

    @suite.teardown
    def teardown_establishment_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

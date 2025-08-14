import requests


def register_tests(suite, test_framework):
    """Register alternative identification tests with the provided test suite"""

    @suite.setup
    def setup_identification_tests(test_framework):
        """Setup tokens for testing alternative identification"""
        try:
            # Get doctor token for doctor operations
            doctor_token = test_framework.login_and_get_token(
                email="alice.brown@example.com",
                password="password3"
            )
            test_framework.doctor_token = doctor_token
        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_create_history_with_doctor_name(test_framework):
        """Test creating medical history using doctor's name instead of ID"""
        new_history = {
            "diagnostic": "Test Condition",
            "treatment": "Test Treatment",
            # Using doctor name instead of ID
            "doctor_first_name": "Alice",
            "doctor_last_name": "Brown",
            "start_date": "2023-03-15",
            "end_date": "2023-04-15"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/history",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_history
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create medical history with doctor name: {
                                 response.status_code}, {response.text}")

        # Verify response
        data = response.json()
        if "history_id" not in data:
            raise AssertionError(
                f"Expected history_id in response, got: {data}")

        # Store for later use
        test_framework.history_id = data["history_id"]

    @suite.test
    def test_create_visit_with_names(test_framework):
        """Test creating a visit using doctor and establishment names"""
        new_visit = {
            # Using establishment name instead of ID
            "establishment_name": "Central City Hospital",
            # Using doctor names instead of ID
            "doctor_first_name": "Alice",
            "doctor_last_name": "Brown",
            "visit_date": "2023-07-15",
            "diagnostic": "Test Visit Condition",
            "treatment": "Test Visit Treatment",
            "summary": "Visit created using doctor and establishment names",
            "notes": "Test notes"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/visits",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_visit
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create visit with names: {
                                 response.status_code}, {response.text}")

        # Verify response contains a visit_id
        data = response.json()
        if "visit_id" not in data:
            raise AssertionError(f"Expected visit_id in response, got: {data}")

        # Store for later use
        test_framework.visit_id = data["visit_id"]

    @suite.test
    def test_invalid_doctor_name(test_framework):
        """Test that providing invalid doctor name returns appropriate error"""
        new_history = {
            "diagnostic": "Test Condition",
            "treatment": "Test Treatment",
            # Using non-existent doctor
            "doctor_first_name": "NonExistent",
            "doctor_last_name": "Doctor",
            "start_date": "2023-03-15",
            "end_date": "2023-04-15"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/history",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_history
        )

        # Should get 400 Bad Request
        if response.status_code != 400:
            raise AssertionError(f"Expected 400 for invalid doctor name, got {
                                 response.status_code}: {response.text}")

        # Verify error message contains information about the problem
        data = response.json()
        if "error" not in data or "Doctor" not in data["error"]:
            raise AssertionError(
                f"Expected error about doctor not found, got: {data}")

    @suite.test
    def test_invalid_establishment_name(test_framework):
        """Test that providing invalid establishment name returns appropriate error"""
        new_visit = {
            # Using non-existent establishment
            "establishment_name": "NonExistent Hospital",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "visit_date": "2023-09-01",
            "diagnostic": "Test Condition",
            "treatment": "Test Treatment",
            "summary": "Test visit with invalid establishment",
            "notes": "Test notes"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/visits",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_visit
        )

        if response.status_code != 400:
            raise AssertionError(f"Expected 400 for invalid establishment name, got {
                                 response.status_code}: {response.text}")

        data = response.json()
        if "error" not in data or "Establishment" not in data["error"]:
            raise AssertionError(
                f"Expected error about establishment not found, got: {data}")

    @suite.teardown
    def teardown_identification_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

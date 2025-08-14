import requests
from datetime import datetime


def register_tests(suite, test_framework):
    """Register API-related tests with the provided test suite"""

    @suite.setup
    def setup_api_tests(test_framework):
        """Setup tokens for testing API endpoints"""
        # Database setup now handled at framework level with transactions

        try:
            admin_token = test_framework.login_and_get_token(
                email="carol.williams@example.com",
                password="password5"
            )
            test_framework.admin_token = admin_token

            patient_token = test_framework.login_and_get_token(
                email="john.doe@example.com",
                password="password1"
            )
            test_framework.patient_token = patient_token
        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_api_patient_get_with_admin_token(test_framework):
        """Test that an admin can get patient details."""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )
        if response.status_code != 200:
            raise AssertionError(f"""
                Failed to get patient with admin token: {response.status_code}, {response.text}
                """)

    @suite.test
    def test_api_patient_get_with_patient_token(test_framework):
        """Test that a patient can get their own details."""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            headers={"Authorization": f"Bearer {test_framework.patient_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"""
                Failed to get patient with patient token: {response.status_code}, {response.text}
                """)

        data = response.json()
        if data.get("first_name") != "John":
            raise AssertionError(f"""
                Expected first_name to be 'John', got {data.get('first_name')}
            """)

    @suite.test
    def test_api_patient_get_no_token(test_framework):
        """Test that unauthorized access is properly rejected."""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456"
        )

        if response.status_code not in [401, 403]:
            raise AssertionError(f"""
                Expected unauthorized access to be rejected with 401 or 403, got {response.status_code}
            """)

    @suite.test
    def test_api_error_handling(test_framework):
        """Test that non-existent endpoints return 404."""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/nonexistent",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 404:
            raise AssertionError(
                f"Expected 404 for non-existent route, got {response.status_code}")

    @suite.test
    def test_api_users_create(test_framework):
        """Test creating a new user(admin-only operation)."""
        unique_email = f"test_user_{datetime.now().timestamp()}@example.com"

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json={
                "login": f"testuser_{datetime.now().timestamp()}",
                "password": "testpassword",
                "user_type": "PATIENT",
                "first_name": "Test",
                "last_name": "User",
                "phone_number": "555-123-4567",
                "email": unique_email
            }
        )

        if response.status_code != 201:
            raise AssertionError(f"""
                Failed to create user: {response.status_code}, {response.text}
                """)

    @suite.teardown
    def teardown_api_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

import requests


def register_tests(suite, test_framework):
    """Register JWT authentication tests with the provided test suite"""

    @suite.setup
    def setup_jwt_tests(test_framework):
        # Database setup now handled at framework level with transactions
        pass

    @suite.test
    def test_successful_login(test_framework):
        """Test that login succeeds with correct credentials and returns a valid JWT token."""
        token = test_framework.assert_login_succeeds(
            email="john.doe@example.com",
            password="password1"
        )
        # Basic validation that we got a token
        test_framework.assert_true(
            len(token) > 20, "Token should be a non-empty string")

    @suite.test
    def test_failed_login_wrong_password(test_framework):
        """Test that login fails with incorrect password."""
        test_framework.assert_login_fails(
            email="john.doe@example.com",
            password="wrong_password"
        )

    @suite.test
    def test_failed_login_nonexistent_user(test_framework):
        """Test that login fails with non-existent user."""
        test_framework.assert_login_fails(
            email="nonexistent@example.com",
            password="password1"
        )

    @suite.test
    def test_protected_route_with_token(test_framework):
        """Test accessing a protected route with a valid token."""
        # First login to get a token
        token = test_framework.login_and_get_token(
            email="john.doe@example.com",
            password="password1"
        )

        # Test access to protected route
        test_framework.assert_protected_route_access(
            url=f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            token=token
        )

    @suite.test
    def test_protected_route_without_token(test_framework):
        """Test that a protected route cannot be accessed without a token."""
        test_framework.assert_protected_route_forbidden(
            url=f"http://localhost:{test_framework.api_port}/api/patients/INS123456"
        )

    @suite.test
    def test_protected_route_with_invalid_token(test_framework):
        """Test that a protected route cannot be accessed with an invalid token."""
        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        test_framework.assert_protected_route_forbidden(
            url=f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            token=invalid_token
        )

    @suite.test
    def test_logout_and_token_blacklisting(test_framework):
        """Test that logout blacklists the token preventing its further use."""
        # First login to get a token
        token = test_framework.login_and_get_token(
            email="john.doe@example.com",
            password="password1"
        )

        # Then verify the token works for a protected route
        test_framework.assert_protected_route_access(
            url=f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            token=token
        )

        # Now logout and verify the token is blacklisted
        test_framework.assert_token_blacklisted(
            token=token,
            url=f"http://localhost:{test_framework.api_port}/api/patients/INS123456"
        )

    @suite.test
    def test_admin_permissions(test_framework):
        """Test that an admin user can access admin-only routes."""
        # First login as admin
        admin_token = test_framework.login_and_get_token(
            email="carol.williams@example.com",
            password="password5"  # Assuming this is admin's password
        )

        # Test that admin can create users
        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "login": "newuser",
                "password": "newpassword",
                "user_type": "PATIENT",
                "first_name": "New",
                "last_name": "User",
                "phone_number": "555-123-4567",
                "email": "newuser@example.com"
            }
        )

        if response.status_code != 201:
            raise AssertionError(f"""
            Admin failed to create user: {response.status_code}, {response.text}
            """)

    @suite.test
    def test_non_admin_permission_denied(test_framework):
        """Test that a non-admin user cannot access admin-only routes."""
        # First login as patient
        patient_token = test_framework.login_and_get_token(
            email="john.doe@example.com",
            password="password1"
        )

        # Test that patient cannot create users
        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/users",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "login": "newuser2",
                "password": "newpassword",
                "user_type": "PATIENT",
                "first_name": "New",
                "last_name": "User",
                "phone_number": "555-123-4567",
                "email": "newuser2@example.com"
            }
        )

        # Should get 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(
                f"Expected non-admin to be denied with 403, "
                f"but got {response.status_code}: {response.text}"
            )

    @suite.test
    def test_patient_self_access(test_framework):
        """Test that patients can access their own data but not others'."""
        # Login as patient
        patient_token = test_framework.login_and_get_token(
            email="john.doe@example.com",
            password="password1"
        )

        # Test access to own data
        test_framework.assert_protected_route_access(
            url=f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            token=patient_token
        )

        # Test access to another patient's data - should be forbidden
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS654321",
            headers={"Authorization": f"Bearer {patient_token}"}
        )

        # Should get 403 Forbidden
        if response.status_code != 403:
            raise AssertionError(
                f"Expected patient to be denied access to another patient's data, "
                f"but got {response.status_code}: {response.text}"
            )

    @suite.teardown
    def teardown_jwt_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

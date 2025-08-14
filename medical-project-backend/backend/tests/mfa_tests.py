import requests
import pyotp


def register_tests(suite, test_framework):
    """Register Multi-Factor Authentication tests with the test suite"""

    @suite.setup
    def setup_mfa_tests(test_framework):
        """Setup tokens and test data for MFA tests"""
        try:
            admin_token = test_framework.login_and_get_token(
                email="carol.williams@example.com",
                password="password5"
            )
            test_framework.admin_token = admin_token

            user_token = test_framework.login_and_get_token(
                email="john.doe@example.com",
                password="password1"
            )
            test_framework.user_token = user_token

            test_framework.test_user_email = "john.doe@example.com"
            test_framework.test_user_password = "password1"

            test_framework.mfa_secret = None
            test_framework.temp_token = None
            test_framework.backup_codes = None

        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_mfa_status_when_not_configured(test_framework):
        """Test checking MFA status when MFA is not configured"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/mfa/status",
            headers={"Authorization": f"Bearer {test_framework.user_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get MFA status: {
                                 response.status_code}, {response.text}")

        data = response.json()
        if data.get("mfa_configured") is not False or data.get("mfa_enabled") is not False:
            raise AssertionError(
                f"Expected MFA to be not configured and not enabled, got: {data}")

    @suite.test
    def test_mfa_setup(test_framework):
        """Test setting up MFA for a user"""
        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/mfa/setup",
            headers={"Authorization": f"Bearer {test_framework.user_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to setup MFA: {
                                 response.status_code}, {response.text}")

        data = response.json()

        if not data.get("secret") or not data.get("provisioning_uri") or not data.get("backup_codes"):
            raise AssertionError(
                f"Missing required fields in MFA setup response: {data}")

        test_framework.mfa_secret = data.get("secret")
        test_framework.backup_codes = data.get("backup_codes")

        provisioning_uri = data.get("provisioning_uri")
        if not provisioning_uri.startswith("otpauth://totp/"):
            raise AssertionError(f"Invalid provisioning URI format: {
                                 provisioning_uri}")

        backup_codes = data.get("backup_codes")
        if len(backup_codes) < 5:  # Should have multiple backup codes
            raise AssertionError(f"Not enough backup codes provided, got {
                                 len(backup_codes)}")

    @suite.test
    def test_mfa_status_after_setup(test_framework):
        """Test checking MFA status after setup but before enabling"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/mfa/status",
            headers={"Authorization": f"Bearer {test_framework.user_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get MFA status: {
                                 response.status_code}, {response.text}")

        data = response.json()
        if data.get("mfa_configured") is not True or data.get("mfa_enabled") is not False:
            raise AssertionError(
                f"Expected MFA to be configured but not enabled, got: {data}")

        if not data.get("configured_at") or not data.get("last_modified"):
            raise AssertionError(
                f"Missing timestamp fields in MFA status: {data}")

    @suite.test
    def test_mfa_enable_with_valid_code(test_framework):
        """Test enabling MFA with a valid TOTP code"""
        if not test_framework.mfa_secret:
            raise AssertionError("No MFA secret available from previous tests")

        totp = pyotp.TOTP(test_framework.mfa_secret)
        valid_code = totp.now()

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/mfa/enable",
            headers={"Authorization": f"Bearer {test_framework.user_token}"},
            json={"code": valid_code}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to enable MFA: {
                                 response.status_code}, {response.text}")

        data = response.json()
        if data.get("status") != "success" or "MFA enabled successfully" not in data.get("message", ""):
            raise AssertionError(
                f"Unexpected response when enabling MFA: {data}")

    @suite.test
    def test_mfa_status_after_enabling(test_framework):
        """Test checking MFA status after enabling MFA"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/mfa/status",
            headers={"Authorization": f"Bearer {test_framework.user_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get MFA status: {
                                 response.status_code}, {response.text}")

        data = response.json()
        if data.get("mfa_configured") is not True or data.get("mfa_enabled") is not True:
            raise AssertionError(
                f"Expected MFA to be configured and enabled, got: {data}")

    @suite.test
    def test_login_with_mfa_enabled(test_framework):
        """Test login flow when MFA is enabled"""
        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/auth/login",
            json={
                "email": test_framework.test_user_email,
                "password": test_framework.test_user_password
            }
        )

        if response.status_code != 200:
            raise AssertionError(
                f"Login failed: {response.status_code}, {response.text}")

        data = response.json()
        if data.get("status") != "MFA Required" or not data.get("temp_token"):
            raise AssertionError(
                f"Expected MFA Required status and temp_token, got: {data}")

        if not data.get("user") or data["user"].get("requires_mfa") is not True:
            raise AssertionError(
                f"User info should indicate MFA is required: {data}")

        test_framework.temp_token = data.get("temp_token")

    @suite.test
    def test_mfa_verify_with_valid_code(test_framework):
        """Test MFA verification with a valid TOTP code"""
        if not test_framework.mfa_secret or not test_framework.temp_token:
            raise AssertionError(
                "Missing MFA secret or temporary token from previous tests")

        # Generate a valid TOTP code
        totp = pyotp.TOTP(test_framework.mfa_secret)
        valid_code = totp.now()

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/mfa/verify",
            headers={"Authorization": f"Bearer {test_framework.temp_token}"},
            json={"code": valid_code}
        )

        if response.status_code != 200:
            raise AssertionError(f"MFA verification failed: {
                                 response.status_code}, {response.text}")

        data = response.json()
        if data.get("status") != "Success" or not data.get("token"):
            raise AssertionError(
                f"Expected Success status and token, got: {data}")

        if not data.get("user") or data["user"].get("requires_mfa") is not False:
            raise AssertionError(
                f"User info should indicate MFA is no longer required: {data}")

        test_framework.user_token = data.get("token")

    @suite.test
    def test_mfa_verify_with_invalid_code(test_framework):
        """Test MFA verification with an invalid TOTP code"""
        if not test_framework.temp_token:
            response = requests.post(
                f"http://localhost:{test_framework.api_port}/api/auth/login",
                json={
                    "email": test_framework.test_user_email,
                    "password": test_framework.test_user_password
                }
            )
            if response.status_code == 200:
                test_framework.temp_token = response.json().get("temp_token")
            else:
                raise AssertionError(f"Failed to get temp token: {
                                     response.status_code}, {response.text}")

        invalid_code = "123456"

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/mfa/verify",
            headers={"Authorization": f"Bearer {test_framework.temp_token}"},
            json={"code": invalid_code}
        )

        if response.status_code != 400:
            raise AssertionError(f"Expected verification with invalid code to fail with 400, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_verify_with_backup_code(test_framework):
        """Test MFA verification with a backup code"""
        if not test_framework.backup_codes or not test_framework.temp_token:
            raise AssertionError(
                "Missing backup codes or temporary token from previous tests")

        backup_code = test_framework.backup_codes[0]

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/mfa/verify",
            headers={"Authorization": f"Bearer {test_framework.temp_token}"},
            json={"code": backup_code}
        )

        if response.status_code != 200:
            raise AssertionError(f"MFA verification with backup code failed: {
                                 response.status_code}, {response.text}")

        data = response.json()
        if data.get("status") != "Success" or not data.get("token"):
            raise AssertionError(
                f"Expected Success status and token, got: {data}")

        test_framework.user_token = data.get("token")

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/auth/login",
            json={
                "email": test_framework.test_user_email,
                "password": test_framework.test_user_password
            }
        )
        if response.status_code == 200:
            test_framework.temp_token = response.json().get("temp_token")

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/mfa/verify",
            headers={"Authorization": f"Bearer {test_framework.temp_token}"},
            json={"code": backup_code}
        )

        # Should be rejected with 400 Bad Request
        if response.status_code != 400:
            raise AssertionError(f"Expected repeated use of backup code to fail with 400, but got {
                                 response.status_code}: {response.text}")

    @suite.test
    def test_disable_mfa(test_framework):
        """Test disabling MFA"""
        if not test_framework.mfa_secret:
            raise AssertionError("No MFA secret available from previous tests")

        totp = pyotp.TOTP(test_framework.mfa_secret)
        valid_code = totp.now()

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/mfa/disable",
            headers={"Authorization": f"Bearer {test_framework.user_token}"},
            json={"code": valid_code}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to disable MFA: {
                                 response.status_code}, {response.text}")

        data = response.json()
        if data.get("status") != "success" or "MFA disabled successfully" not in data.get("message", ""):
            raise AssertionError(
                f"Unexpected response when disabling MFA: {data}")

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/mfa/status",
            headers={"Authorization": f"Bearer {test_framework.user_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get MFA status: {
                                 response.status_code}, {response.text}")

        status_data = response.json()
        if status_data.get("mfa_enabled") is not False:
            raise AssertionError(
                f"Expected MFA to be disabled, got: {status_data}")

    @suite.test
    def test_login_after_mfa_disabled(test_framework):
        """Test login flow after MFA has been disabled"""
        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/auth/login",
            json={
                "email": test_framework.test_user_email,
                "password": test_framework.test_user_password
            }
        )

        if response.status_code != 200:
            raise AssertionError(
                f"Login failed: {response.status_code}, {response.text}")

        data = response.json()
        if data.get("status") != "Success" or not data.get("token"):
            raise AssertionError(
                f"Expected Success status and token, got: {data}")

        if not data.get("user") or data["user"].get("requires_mfa") is True:
            raise AssertionError(
                f"User info should indicate MFA is not required: {data}")

    @suite.test
    def test_disable_mfa_with_invalid_code(test_framework):
        """Test attempting to disable MFA with an invalid code"""
        if not test_framework.mfa_secret:
            raise AssertionError("No MFA secret available from previous tests")

        totp = pyotp.TOTP(test_framework.mfa_secret)
        valid_code = totp.now()

        requests.post(
            f"http://localhost:{test_framework.api_port}/api/mfa/enable",
            headers={"Authorization": f"Bearer {test_framework.user_token}"},
            json={"code": valid_code}
        )

        invalid_code = "000000"

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/mfa/disable",
            headers={"Authorization": f"Bearer {test_framework.user_token}"},
            json={"code": invalid_code}
        )

        if response.status_code != 400:
            raise AssertionError(f"Expected disabling with invalid code to fail with 400, but got {
                                 response.status_code}: {response.text}")

        valid_code = totp.now()
        requests.post(
            f"http://localhost:{test_framework.api_port}/api/mfa/disable",
            headers={"Authorization": f"Bearer {test_framework.user_token}"},
            json={"code": valid_code}
        )

    @suite.teardown
    def teardown_mfa_tests(test_framework):
        """Clean up after MFA tests"""
        try:
            if test_framework.mfa_secret:
                totp = pyotp.TOTP(test_framework.mfa_secret)
                valid_code = totp.now()

                response = requests.post(
                    f"http://localhost:{test_framework.api_port}/api/mfa/disable",
                    headers={"Authorization": f"Bearer {
                        test_framework.user_token}"},
                    json={"code": valid_code}
                )

                if response.status_code == 200:
                    print("Successfully disabled MFA during test cleanup")
                else:
                    print(f"Warning: Failed to disable MFA during test cleanup: {
                          response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error during MFA test cleanup: {str(e)}")

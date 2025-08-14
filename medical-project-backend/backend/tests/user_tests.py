def register_tests(suite, test_framework):
    """Register user-related tests with the provided test suite"""

    @suite.setup
    def setup_user_tests(test_framework):
        # Database setup now handled at framework level with transactions
        pass

    @suite.test
    def test_user_creation(test_framework):
        test_framework.assert_record_exists("users", {"login": "patient1"})

    @suite.test
    def test_user_medical_history(test_framework):
        test_framework.assert_record_exists(
            "medical_history",
            {"patient_id": "INS123456", "diagnostic": "Hypertension"}
        )

    @suite.teardown
    def teardown_user_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

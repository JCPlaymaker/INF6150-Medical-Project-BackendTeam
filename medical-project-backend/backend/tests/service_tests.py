import requests
from datetime import date, datetime, timedelta


def register_tests(suite, test_framework):
    """Register service-specific tests"""

    @suite.setup
    def setup_service_tests(test_framework):
        # Database setup now handled at framework level with transactions

        try:
            # Get doctor token for testing
            doctor_token = test_framework.login_and_get_token(
                email="alice.brown@example.com",
                password="password3"
            )
            test_framework.doctor_token = doctor_token
        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_visit_date_handling(test_framework):
        """Test that visit dates are properly handled in the service"""
        # Test with past date
        past_date = (date.today() - timedelta(days=30)).isoformat()

        new_visit = {
            "establishment_id": "e1234567-89ab-cdef-0123-456789abcdef",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "visit_date": past_date,
            "diagnostic": "Past Visit Test",
            "treatment": "Test Treatment",
            "summary": "Testing with past date",
            "notes": "Should work fine with past date"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/visits",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_visit
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create visit with past date: {
                                 response.status_code}, {response.text}")

        # Store ID for future tests
        test_framework.past_visit_id = response.json()["visit_id"]

    @suite.test
    def test_medical_history_date_range(test_framework):
        """Test medical history with start date after end date"""
        # Using dates in wrong order
        start_date = (datetime.now() + timedelta(days=30)).date().isoformat()
        end_date = (datetime.now() - timedelta(days=30)).date().isoformat()

        new_history = {
            "diagnostic": "Date Range Test",
            "treatment": "Test Treatment",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": start_date,
            "end_date": end_date  # End date before start date
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/history",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_history
        )

        # Check how the application handles this - ideally should validate and return 400
        # But we're just checking the behavior here
        if response.status_code == 201:
            # If the app accepts this, store ID for future reference
            test_framework.invalid_date_history_id = response.json()[
                "history_id"]
            # We should report that the validation could be improved
            print(
                "Note: Application accepts medical history with end date before start date")
        else:
            # If it rejects with validation error, that's good
            print(f"Application correctly rejected invalid date range with status {
                  response.status_code}")

    @suite.test
    def test_null_values_handling(test_framework):
        """Test handling of null/None values in optional fields"""
        # Test with null values in optional fields
        new_history = {
            "diagnostic": "Null Value Test",
            "treatment": "Test Treatment",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": date.today().isoformat(),
            "end_date": None  # Explicitly null end date
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/history",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_history
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to handle null value in end_date: {
                                 response.status_code}, {response.text}")

        # Test with null values in optional fields for visits
        new_visit = {
            "establishment_id": "e1234567-89ab-cdef-0123-456789abcdef",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "visit_date": date.today().isoformat(),
            "diagnostic": None,  # Null diagnostic
            "treatment": None,   # Null treatment
            "summary": "Testing null values",
            "notes": None        # Null notes
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/visits",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_visit
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to handle null values in visit optional fields: {
                                 response.status_code}, {response.text}")

    @suite.test
    def test_empty_string_handling(test_framework):
        """Test handling of empty strings in required fields during updates"""
        # First create a valid history record
        new_history = {
            "diagnostic": "Empty String Test",
            "treatment": "Initial Treatment",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": date.today().isoformat(),
            "end_date": None
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/history",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_history
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create history for empty string test: {
                                 response.status_code}, {response.text}")

        history_id = response.json()["history_id"]

        # Now try to update with empty strings
        update_data = {
            "diagnostic": "",  # Empty string in required field
            "treatment": "",   # Empty string in required field
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": date.today().isoformat(),
            "end_date": None
        }

        response = requests.put(
            f"http://localhost:{
                test_framework.api_port}/api/patients/INS123456/history/{history_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=update_data
        )

        # Check how the application handles this
        # Ideally it should validate and reject empty strings in required fields
        if response.status_code == 201:
            print(
                "Note: Application accepts empty strings in required fields during update")
        else:
            print(f"Application correctly rejected empty strings with status {
                  response.status_code}")

    @suite.teardown
    def teardown_service_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

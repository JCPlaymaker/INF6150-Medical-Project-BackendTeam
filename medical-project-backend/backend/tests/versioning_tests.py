import requests
import time
from datetime import datetime


def register_tests(suite, test_framework):
    """Register versioning system tests with the provided test suite"""

    @suite.setup
    def setup_versioning_tests(test_framework):
        """Setup tokens for testing versioning functionality"""
        try:
            admin_token = test_framework.login_and_get_token(
                email="carol.williams@example.com",
                password="password5"
            )
            test_framework.admin_token = admin_token

            doctor_token = test_framework.login_and_get_token(
                email="alice.brown@example.com",
                password="password3"
            )
            test_framework.doctor_token = doctor_token

            patient_token = test_framework.login_and_get_token(
                email="john.doe@example.com",
                password="password1"
            )
            test_framework.patient_token = patient_token
        except Exception as e:
            raise AssertionError(f"Failed to obtain test tokens: {str(e)}")

    @suite.test
    def test_patient_basic_versioning(test_framework):
        """Test basic patient versioning - update and verify latest version is returned"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get initial patient state: {
                                 response.status_code}, {response.text}")

        initial_data = response.json()
        initial_first_name = initial_data["first_name"]
        initial_phone = initial_data["phone_number"]
        initial_dob = initial_data.get("date_of_birth")

        timestamp = int(time.time())
        new_first_name = f"Updated{timestamp}"
        new_phone = f"555-{timestamp}-9999"
        new_dob = "1992-08-20"

        update_data = {
            "login": initial_data["login"],
            "gender": initial_data["gender"],
            "city_of_birth": initial_data["city_of_birth"],
            "first_name": new_first_name,
            "last_name": initial_data["last_name"],
            "phone_number": new_phone,
            "email": initial_data["email"],
            "date_of_birth": new_dob
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=update_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to update patient: {
                                 response.status_code}, {response.text}")

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get updated patient: {
                                 response.status_code}, {response.text}")

        updated_data = response.json()

        if updated_data["first_name"] != new_first_name:
            raise AssertionError(f"Expected first_name to be updated to '{
                                 new_first_name}', but got '{updated_data['first_name']}'")

        if updated_data["phone_number"] != new_phone:
            raise AssertionError(f"Expected phone_number to be updated to '{
                                 new_phone}', but got '{updated_data['phone_number']}'")

        if "date_of_birth" in updated_data:
            updated_dob = updated_data["date_of_birth"]
            year, month, day = new_dob.split("-")

            if (year not in updated_dob or
                day.lstrip("0") not in updated_dob or
                    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][int(month)-1] not in updated_dob):
                raise AssertionError(f"Expected date_of_birth to contain year={year}, month={
                                     month} and day={day}, but got '{updated_dob}'")

        if updated_data["user_id"] != initial_data["user_id"]:
            raise AssertionError(
                f"Expected user_id to remain the same after update")

        print(f"Successfully verified basic patient versioning")

    @suite.test
    def test_multiple_patient_updates(test_framework):
        """Test multiple sequential updates to a patient"""
        timestamps = []
        names = []
        dates_of_birth = ["1991-03-15", "1992-07-22",
                          "1993-11-30"]  # Test different dates

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS654321",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get initial patient state: {
                                 response.status_code}, {response.text}")

        initial_data = response.json()

        for i in range(3):
            timestamp = int(time.time())
            timestamps.append(timestamp)
            new_name = f"Name{timestamp}-{i}"
            names.append(new_name)

            update_data = {
                "login": initial_data["login"],
                "gender": initial_data["gender"],
                "city_of_birth": initial_data["city_of_birth"],
                "first_name": new_name,
                "last_name": initial_data["last_name"],
                "phone_number": initial_data["phone_number"],
                "email": initial_data["email"],
                "date_of_birth": dates_of_birth[i]
            }

            response = requests.put(
                f"http://localhost:{test_framework.api_port}/api/patients/INS654321",
                headers={"Authorization": f"Bearer {
                    test_framework.admin_token}"},
                json=update_data
            )

            if response.status_code != 201:
                raise AssertionError(f"Failed to update patient (iteration {i}): {
                                     response.status_code}, {response.text}")

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS654321",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get final patient state: {
                                 response.status_code}, {response.text}")

        final_data = response.json()

        if final_data["first_name"] != names[-1]:
            raise AssertionError(f"Expected first_name to be '{
                                 names[-1]}' (latest update), but got '{final_data['first_name']}'")

        if "date_of_birth" in final_data:
            updated_dob = final_data["date_of_birth"]
            year, month, day = dates_of_birth[-1].split("-")

            if (year not in updated_dob or
                day.lstrip("0") not in updated_dob or  # Remove leading zero
                    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][int(month)-1] not in updated_dob):
                raise AssertionError(f"Expected date_of_birth to contain year={year}, month={
                                     month} and day={day}, but got '{updated_dob}'")

        print(f"Successfully verified multiple patient updates versioning")

    @suite.test
    def test_related_entities_versioning(test_framework):
        """Test versioning for related entities (coordinates, medical history, visits)"""
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get patient with coordinates: {
                                 response.status_code}, {response.text}")

        initial_data = response.json()
        if not initial_data.get("coordinates"):
            raise AssertionError("Patient has no coordinates to test with")

        timestamp = int(time.time())
        new_history = {
            "diagnostic": f"Diagnostic-{timestamp}",
            "treatment": f"Treatment-{timestamp}",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": "2023-01-01",
            "end_date": "2023-01-15"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/history",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_history
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create medical history: {
                                 response.status_code}, {response.text}")

        history_id = response.json()["history_id"]

        updated_history = {
            "diagnostic": f"Updated-Diagnostic-{timestamp}",
            "treatment": f"Updated-Treatment-{timestamp}",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "start_date": "2023-01-01",
            "end_date": "2023-01-30"  # Changed end date
        }

        response = requests.put(
            f"http://localhost:{
                test_framework.api_port}/api/patients/INS123456/history/{history_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=updated_history
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to update medical history: {
                                 response.status_code}, {response.text}")

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get patient with updated history: {
                                 response.status_code}, {response.text}")

        updated_data = response.json()

        # Find the history entry we updated
        found_updated_history = False
        for history in updated_data["medical_history"]:
            if history["id"] == history_id:
                found_updated_history = True
                if history["diagnostic"] != updated_history["diagnostic"]:
                    raise AssertionError(f"Expected diagnostic to be updated to '{
                                         updated_history['diagnostic']}', but got '{history['diagnostic']}'")
                if history["treatment"] != updated_history["treatment"]:
                    raise AssertionError(f"Expected treatment to be updated to '{
                                         updated_history['treatment']}', but got '{history['treatment']}'")
                break

        if not found_updated_history:
            raise AssertionError(
                f"Could not find the updated medical history record in patient data")

        print(f"Successfully verified related entities versioning")

    @suite.test
    def test_medical_visits_versioning(test_framework):
        """Test versioning for medical visits"""
        # Step 1: Create a new medical visit
        timestamp = int(time.time())
        new_visit = {
            "establishment_id": "e1234567-89ab-cdef-0123-456789abcdef",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "visit_date": "2023-09-01",
            "diagnostic": f"Initial-Visit-Diagnostic-{timestamp}",
            "treatment": f"Initial-Visit-Treatment-{timestamp}",
            "summary": f"Initial visit summary {timestamp}",
            "notes": "Initial notes"
        }

        response = requests.post(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456/visits",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=new_visit
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to create medical visit: {
                                 response.status_code}, {response.text}")

        visit_id = response.json()["visit_id"]

        # Step 2: Update the medical visit
        updated_visit = {
            "establishment_id": "e1234567-89ab-cdef-0123-456789abcdef",
            "doctor_id": "2d3cfc26-4958-4723-acf8-9799502c4d7d",
            "visit_date": "2023-09-01",
            "diagnostic": f"Updated-Visit-Diagnostic-{timestamp}",
            "treatment": f"Updated-Visit-Treatment-{timestamp}",
            "summary": f"Updated visit summary {timestamp}",
            "notes": "Updated notes"
        }

        response = requests.put(
            f"http://localhost:{
                test_framework.api_port}/api/patients/INS123456/visits/{visit_id}",
            headers={"Authorization": f"Bearer {test_framework.doctor_token}"},
            json=updated_visit
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to update medical visit: {
                                 response.status_code}, {response.text}")

        # Step 3: Get the patient again and check for the updated visit
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get patient with updated visit: {
                                 response.status_code}, {response.text}")

        patient_data = response.json()

        # Find the visit we updated
        found_updated_visit = False
        for visit in patient_data["medical_visits"]:
            if visit["id"] == visit_id:
                found_updated_visit = True
                if visit["diagnostic_established"] != updated_visit["diagnostic"]:
                    raise AssertionError(f"Expected diagnostic to be updated to '{
                                         updated_visit['diagnostic']}', but got '{visit['diagnostic_established']}'")
                if visit["treatment"] != updated_visit["treatment"]:
                    raise AssertionError(f"Expected treatment to be updated to '{
                                         updated_visit['treatment']}', but got '{visit['treatment']}'")
                if visit["visit_summary"] != updated_visit["summary"]:
                    raise AssertionError(f"Expected summary to be updated to '{
                                         updated_visit['summary']}', but got '{visit['visit_summary']}'")
                break

        if not found_updated_visit:
            raise AssertionError(
                f"Could not find the updated medical visit in patient data")

        print(f"Successfully verified medical visits versioning")

    @suite.test
    def test_date_of_birth_update_format(test_framework):
        """Test specific handling of date_of_birth field updates"""
        # This test specifically targets the date_of_birth field to ensure it's being handled correctly

        # Step 1: Get a patient
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS789012",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get patient: {
                                 response.status_code}, {response.text}")

        initial_data = response.json()
        initial_dob = initial_data.get("date_of_birth")

        # Step 2: Update with a new date_of_birth
        new_dob = "2000-12-31"  # Use a specific date

        update_data = {
            "login": initial_data["login"],
            "gender": initial_data["gender"],
            "city_of_birth": initial_data["city_of_birth"],
            "first_name": initial_data["first_name"],
            "last_name": initial_data["last_name"],
            "phone_number": initial_data["phone_number"],
            "email": initial_data["email"],
            "date_of_birth": new_dob
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/patients/INS789012",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=update_data
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed to update patient with new date_of_birth: {
                                 response.status_code}, {response.text}")

        # Step 3: Get the patient again
        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS789012",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get updated patient: {
                                 response.status_code}, {response.text}")

        updated_data = response.json()

        # Verify the date_of_birth was updated - using the same format-aware check
        if "date_of_birth" in updated_data:
            returned_dob = updated_data["date_of_birth"]
            # Extract parts from new_dob (2000-12-31)
            year, month, day = new_dob.split("-")

            # Check if all components of the date are in the formatted string
            if (year not in returned_dob or
                day.lstrip("0") not in returned_dob or  # Remove leading zero
                    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][int(month)-1] not in returned_dob):
                raise AssertionError(f"Expected date_of_birth to contain year={year}, month={
                                     month} and day={day}, but got '{returned_dob}'")
        else:
            raise AssertionError(
                f"date_of_birth field is missing in the response")

        print(f"Successfully verified date_of_birth field update")

    @suite.test
    def test_query_version_selection_mechanism(test_framework):
        """Test that the query correctly selects the latest version of records"""

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        initial_data = response.json()

        timestamp1 = int(time.time())
        update_data1 = {
            "login": initial_data["login"],
            "gender": initial_data["gender"],
            "city_of_birth": initial_data["city_of_birth"],
            "first_name": f"FirstUpdate{timestamp1}",
            "last_name": initial_data["last_name"],
            "phone_number": initial_data["phone_number"],
            "email": initial_data["email"],
            "date_of_birth": "1995-07-15"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=update_data1
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed first update: {
                                 response.status_code}, {response.text}")

        timestamp2 = int(time.time())
        update_data2 = {
            "login": initial_data["login"],
            "gender": initial_data["gender"],
            "city_of_birth": initial_data["city_of_birth"],
            "first_name": f"SecondUpdate{timestamp2}",
            "last_name": initial_data["last_name"],
            "phone_number": initial_data["phone_number"],
            "email": initial_data["email"],
            "date_of_birth": "1995-07-15"
        }

        response = requests.put(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"},
            json=update_data2
        )

        if response.status_code != 201:
            raise AssertionError(f"Failed second update: {
                                 response.status_code}, {response.text}")

        response = requests.get(
            f"http://localhost:{test_framework.api_port}/api/patients/INS123456",
            headers={"Authorization": f"Bearer {test_framework.admin_token}"}
        )

        if response.status_code != 200:
            raise AssertionError(f"Failed to get patient after updates: {
                                 response.status_code}, {response.text}")

        final_data = response.json()

        if final_data["first_name"] != update_data2["first_name"]:
            raise AssertionError(f"Expected first_name to be '{
                                 update_data2['first_name']}' (latest update), but got '{final_data['first_name']}'")

        if final_data["first_name"] == update_data1["first_name"]:
            raise AssertionError(f"Got the first update's value ('{
                                 update_data1['first_name']}') instead of the second update's value")

        print("Successfully verified query version selection mechanism")

    @suite.teardown
    def teardown_versioning_tests(test_framework):
        # No database cleanup needed - transactions handle this
        pass

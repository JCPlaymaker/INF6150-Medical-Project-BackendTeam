from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import track
from datetime import datetime
from typing import Callable, List, Dict, Any, Optional
import requests
import os
import sys
import time


class TestResult:
    def __init__(self, name: str, passed: bool, error: Optional[str] = None, duration: float = 0):
        self.name = name
        self.passed = passed
        self.error = error
        self.duration = duration


class TestSuite:
    def __init__(self, name: str):
        self.name = name
        self.tests: List[Callable] = []
        self.setup_functions: List[Callable] = []
        self.teardown_functions: List[Callable] = []
        self.results: List[TestResult] = []

    def test(self, func: Callable):
        self.tests.append(func)
        return func

    def setup(self, func: Callable):
        self.setup_functions.append(func)
        return func

    def teardown(self, func: Callable):
        self.teardown_functions.append(func)
        return func


class TestFramework:
    def __init__(self, db_instance, api_port):
        self.db_instance = db_instance
        self.api_port = api_port
        self.suites: Dict[str, TestSuite] = {}
        self.start_time = None
        self.end_time = None
        self.console = Console()

        # Cache for tokens to avoid repeated logins
        self._token_cache = {}

        # Flag to track if database has been initialized
        self.db_initialized = False

        # Transaction isolation
        self.use_transactions = True

    def create_suite(self, name: str) -> TestSuite:
        suite = TestSuite(name)
        self.suites[name] = suite
        return suite

    def assert_equals(self, expected: Any, actual: Any, message: Optional[str] = None):
        if expected != actual:
            raise AssertionError(
                f"{message or 'Assertion failed:'} expected"
                f"{expected}, but got {actual}"
            )

    def assert_true(self, condition: bool, message: Optional[str] = None):
        if not condition:
            raise AssertionError(message or "Expected True but got False")

    def assert_false(self, condition: bool, message: Optional[str] = None):
        if condition:
            raise AssertionError(message or "Expected False but got True")

    def assert_record_exists(self, table: str, conditions: Dict[str, Any]):
        with self.db_instance.get_conn() as conn:
            with conn.cursor() as cur:
                where_clause = " AND ".join(
                    [f"{k} = %s" for k in conditions.keys()])
                query = f"SELECT COUNT(*) FROM {table} WHERE {where_clause}"

                cur.execute(query, list(conditions.values()))
                count = cur.fetchone()[0]

        if count == 0:
            raise AssertionError(f"No record found in"
                                 f"{table} matching conditions: {conditions}")

    def assert_http_status(self, url: str, expected_status: int, message: Optional[str] = None):
        try:
            response = requests.get(url)
            if response.status_code != expected_status:
                raise AssertionError(
                    message or f"Expected status code {expected_status} "
                    f"but got {response.status_code} for URL: {url}"
                )
        except requests.RequestException as e:
            raise AssertionError(f"Request failed: {str(e)}")

    def assert_json_response(self, url: str, key: str, expected_value: Any, message: Optional[str] = None):
        try:
            response = requests.get(url)
            response.raise_for_status()

            try:
                json_data = response.json()
            except requests.exceptions.JSONDecodeError:
                raise AssertionError(f"Response from {url} is not valid JSON")

            if key not in json_data:
                raise AssertionError(
                    message or f"Key '{key}'"
                    f"not found in JSON response from URL: {url}"
                )

            actual_value = json_data[key]
            if actual_value != expected_value:
                raise AssertionError(
                    message or f"Expected value '{expected_value}' for key "
                    f"'{key}' but got '{actual_value}' from URL: {url}"
                )
        except requests.RequestException as e:
            raise AssertionError(f"Request failed for URL {url}: {str(e)}")

    def login_and_get_token(self, email: str, password: str, force_refresh: bool = True) -> str:
        """Attempt to login and return the token if successful, with caching"""
        # Check if token is already in cache and not forcing refresh
        cache_key = f"{email}:{password}"
        if not force_refresh and cache_key in self._token_cache:
            return self._token_cache[cache_key]

        # If not in cache or forcing refresh, perform login
        try:
            response = requests.post(
                f"http://localhost:{self.api_port}/api/auth/login",
                json={"email": email, "password": password}
            )
            if response.status_code != 200:
                raise AssertionError(f"Login failed with status code {
                    response.status_code}: {response.text}")

            data = response.json()
            if "token" not in data:
                raise AssertionError(
                    f"Login succeeded but no token returned: {data}")

            # Cache the token for future use
            self._token_cache[cache_key] = data["token"]
            return data["token"]
        except requests.RequestException as e:
            raise AssertionError(f"Request failed during login: {str(e)}")

    def assert_login_succeeds(self, email: str, password: str, message: Optional[str] = None):
        """Assert that login is successful and returns a token"""
        try:
            response = requests.post(
                f"http://localhost:{self.api_port}/api/auth/login",
                json={"email": email, "password": password}
            )
            if response.status_code != 200:
                raise AssertionError(
                    message or f"Login failed with status code {
                        response.status_code}: {response.text}"
                )
            data = response.json()
            if "token" not in data:
                raise AssertionError(
                    message or f"Login succeeded but no token returned: {data}"
                )
            if "user" not in data:
                raise AssertionError(
                    message or f"Login succeeded but no user data returned: {
                        data}"
                )
            token_parts = data["token"].split('.')
            if len(token_parts) != 3:
                raise AssertionError(
                    message or f"Token is not in valid JWT format: {
                        data['token']}"
                )

            # Cache the token
            cache_key = f"{email}:{password}"
            self._token_cache[cache_key] = data["token"]

            return data["token"]
        except requests.RequestException as e:
            raise AssertionError(f"Request failed: {str(e)}")

    def assert_login_fails(self, email: str, password: str, expected_status: int = 401, message: Optional[str] = None):
        """Assert that login fails with the expected status code"""
        try:
            response = requests.post(
                f"http://localhost:{self.api_port}/api/auth/login",
                json={"email": email, "password": password}
            )

            if response.status_code != expected_status:
                raise AssertionError(
                    message or f"Expected login to fail with status {
                        expected_status} "
                    f"but got {response.status_code}: {response.text}"
                )
        except requests.RequestException as e:
            raise AssertionError(f"Request failed: {str(e)}")

    def assert_protected_route_access(self, url: str, token: str, message: Optional[str] = None):
        """Assert that a protected route can be accessed with the token"""
        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code != 200:
                raise AssertionError(
                    message or f"Failed to access protected route {url} "
                    f"with status code {response.status_code}: {response.text}"
                )
        except requests.RequestException as e:
            raise AssertionError(f"Request failed: {str(e)}")

    def assert_protected_route_forbidden(self, url: str, token: str = "", expected_status: int = 401, message: Optional[str] = None):
        """Assert that a protected route cannot be accessed without a valid token"""
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"

            response = requests.get(url, headers=headers)

            if response.status_code != expected_status:
                raise AssertionError(
                    message or f"Expected protected route {
                        url} to return status {expected_status} "
                    f"but got {response.status_code}: {response.text}"
                )
        except requests.RequestException as e:
            raise AssertionError(f"Request failed: {str(e)}")

    def assert_token_blacklisted(self, token: str, url: str, message: Optional[str] = None):
        """
        Assert that a token has been blacklisted by:
        1. Logging out with the token
        2. Attempting to access a protected route with the token
        """
        try:
            logout_response = requests.post(
                f"http://localhost:{self.api_port}/api/auth/logout",
                headers={"Authorization": f"Bearer {token}"}
            )

            if logout_response.status_code != 200:
                raise AssertionError(
                    message or f"Logout failed with status code {
                        logout_response.status_code}: {logout_response.text}"
                )

            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code != 401:
                raise AssertionError(
                    message or f"Expected blacklisted token to be rejected with status 401 "
                    f"but got {response.status_code}: {response.text}"
                )
        except requests.RequestException as e:
            raise AssertionError(f"Request failed: {str(e)}")

    def setup_database_once(self):
        """Setup database only if it hasn't been initialized already"""
        if not self.db_initialized:
            console = self.console
            with console.status("[bold green]Setting up test database (one-time)...") as status:
                # First drop any existing tables to ensure clean start
                self.db_instance.drop_indexes(False)
                self.db_instance.drop_tables(False)

                # Initialize database structures
                self.db_instance.initialize_extensions()
                status.update("[bold green]Extensions initialized...")

                self.db_instance.initialize_tables()
                status.update("[bold green]Tables initialized...")

                self.db_instance.initialize_indexes()
                status.update("[bold green]Indexes initialized...")

                # Insert test data
                self.insert_test_data_with_status(status)

            console.print("✅ [bold green]Database setup complete!")
            self.db_initialized = True
        else:
            self.console.print("[bold blue]Using existing database setup")

    def setup_database(self):
        """Legacy method, now just calls setup_database_once for backward compatibility"""
        self.setup_database_once()

    def insert_test_data_with_status(self, status=None):
        """Insert test data with optional status updates"""
        if status is None:
            status = self.console.status("[bold green]Inserting test data...")
            status_created = True
        else:
            status_created = False

        with status:
            test_data_files = [
                "data/establishments.json",
                "data/users.json",
                "data/coordinates.json",
                "data/parents.json",
                "data/medical_history.json",
                "data/medical_visits.json"
            ]

            total_files = len(test_data_files)
            for index, file in enumerate(test_data_files, 1):
                data_path = Path(file)
                if data_path.exists():
                    self.db_instance.add_test_data(str(data_path))
                    percentage = (index / total_files) * 100
                    status.update(f"[bold green]Progress: {
                                  percentage:.0f}% - Inserted {file}")

        if status_created:
            self.console.print(
                "[bold green]✅ All test data inserted successfully!")

    def insert_test_data(self):
        """Legacy method for backward compatibility"""
        if not self.db_initialized:
            self.insert_test_data_with_status()
        # Otherwise, do nothing as data is already loaded

    def begin_transaction(self):
        """Start a database transaction for test isolation"""
        if self.use_transactions:
            with self.db_instance.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("BEGIN;")
                conn.commit()  # Commit the BEGIN command

    def rollback_transaction(self):
        """Rollback the current transaction to undo test changes"""
        if self.use_transactions:
            with self.db_instance.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("ROLLBACK;")
                conn.commit()  # Commit the ROLLBACK command

    def run_all_tests(self):
        """Run all registered tests with optimized database handling"""
        console = self.console
        self.start_time = datetime.now()
        total_tests = sum(len(suite.tests) for suite in self.suites.values())

        console.print("\n[bold cyan]🚀 Starting test execution...\n")

        # One-time database setup for all tests
        self.setup_database_once()

        results_table = Table(show_header=True, header_style="bold magenta")
        results_table.add_column("Suite")
        results_table.add_column("Test")
        results_table.add_column("Status")
        results_table.add_column("Duration")
        results_table.add_column("Error")

        for suite_name, suite in self.suites.items():
            console.print(f"[bold yellow]Running suite: {suite_name}")

            # Run suite-level setup once
            for setup in suite.setup_functions:
                setup(self)

            for test in suite.tests:
                # Begin transaction for each test for isolation
                self.begin_transaction()

                start = datetime.now()
                try:
                    test(self)
                    duration = (datetime.now() - start).total_seconds()
                    results_table.add_row(
                        suite_name,
                        test.__name__,
                        "✅ PASS",
                        f"{duration:.2f}s",
                        ""
                    )
                    suite.results.append(TestResult(
                        test.__name__, True, duration=duration))
                except Exception as e:
                    duration = (datetime.now() - start).total_seconds()
                    error_text = Text(str(e), style="red")
                    results_table.add_row(
                        suite_name,
                        test.__name__,
                        "❌ FAIL",
                        f"{duration:.2f}s",
                        str(error_text)
                    )
                    suite.results.append(TestResult(
                        test.__name__, False, str(error_text), duration))
                finally:
                    # Roll back transaction to clean up test data changes
                    self.rollback_transaction()

            # Run suite-level teardown
            for teardown in suite.teardown_functions:
                teardown(self)

        self.end_time = datetime.now()

        console.print("\n[bold white]Test Results:[/bold white]")
        console.print(results_table)

        total_duration = (self.end_time - self.start_time).total_seconds()
        total_passed = sum(
            sum(1 for r in suite.results if r.passed)
            for suite in self.suites.values()
        )

        summary = f"""
        Total Tests: {total_tests}
        Passed: {total_passed}
        Failed: {total_tests - total_passed}
        Duration: {total_duration:.2f}s
        """

        console.print(
            Panel(summary, title="[bold cyan]Summary", border_style="cyan"))

    def cleanup_database(self):
        """Clean up database - now optional and typically only called at the very end"""
        console = self.console
        with console.status("[bold red]Cleaning up test database...") as status:
            self.db_instance.drop_indexes(False)
            self.db_instance.drop_tables(False)

            # Reset initialization flag
            self.db_initialized = False

        console.print("✅ [bold green]Database cleanup complete!")

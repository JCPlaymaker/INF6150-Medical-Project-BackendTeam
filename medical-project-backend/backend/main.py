from tests.test_runner import run_tests
import typer
from app import create_app
from app.config import Config
from app.db import Database
from pathlib import Path
import os
from dotenv import load_dotenv
import sys
from tests.test_framework import TestFramework
import requests
from datetime import datetime

app = typer.Typer(add_completion=False)


@app.command()
def serve(config_file: str = "config.toml"):
    """
    Start the HTTP server on the specified port.
    """
    flask_app = create_app(config_file)
    port = os.getenv("INF6150_API_PORT")
    if port is not None:
        flask_app.run(host="0.0.0.0", port=int(port))


@app.command()
def serve_test(config_file: str = "config.toml"):
    """
    Start the HTTP server on the specified port.
    """
    flask_app = create_app(config_file, use_test_db=True)
    port = os.getenv("INF6150_API_PORT")
    if port is not None:
        flask_app.run(host="0.0.0.0", port=int(port))


@app.command()
def db(command: str = typer.Argument(..., help="Database command: init, drop, add"),
       test_data: str = typer.Option(
        "All", "--test-data", "-t"),
        config_file: str = "config.toml"):
    """
    Perform database operations: init, drop, add <testData>.
    """

    load_dotenv()

    user = os.getenv("INF6150_DATABASE_USER")
    password = os.getenv("INF6150_DATABASE_PASSWORD")

    in_container = os.getenv("INF6150_SERVER_IN_CONTAINER",
                             'True').lower() in ('true', '1', 't')
    if in_container:
        host = os.getenv("INF6150_DATABASE_DOCKER_HOST")
        port = os.getenv("INF6150_DATABASE_DOCKER_PORT")
    else:
        host = os.getenv("INF6150_DATABASE_HOST")
        port = os.getenv("INF6150_DATABASE_PORT")

    database = os.getenv("INF6150_DATABASE_NAME")
    db_instance = Database(user, password, host, port, database)

    try:
        if command == "init":
            db_instance.initialize_extensions()
            db_instance.initialize_tables()
            db_instance.initialize_indexes()
        elif command == "drop":
            # confirmation = typer.confirm(
            #     "Are you sure you want to drop all tables?")
            # if confirmation:
            db_instance.drop_indexes()
            db_instance.drop_tables()
            # else:
            # typer.echo("Drop operation cancelled.")
        elif command == "add":
            if test_data and test_data != "All":
                data_path = Path(test_data)
                if not data_path.exists():
                    typer.echo(f"Test data file '{test_data}' does not exist.")
                    sys.exit(1)
                db_instance.add_test_data(str(data_path))
            elif test_data and test_data == "All":
                data_dir = Path('data')
                test_files = [
                    'establishments.json',
                    'users.json',
                    'coordinates.json',
                    'medical_history.json',
                    'medical_visits.json',
                    'parents.json'
                ]
                for filename in test_files:
                    data_path = data_dir / filename
                    if data_path.exists():
                        typer.echo(f"Adding test data from '{data_path}'...")
                        db_instance.add_test_data(str(data_path))
                    else:
                        typer.echo(
                            f"Warning: Test data file '{data_path}' "
                            "does not exist. Skipping."
                        )
                typer.echo("All available test data files have been added.")
        else:
            typer.echo(f"Unknown command '{command}'. "
                       " Use 'init', 'drop', or 'add'.")
    except Exception as e:
        typer.echo(f"An error occurred: {e}")
    finally:
        db_instance.close_pool()


@app.command()
def test(cleanup: bool = typer.Option(False, "--cleanup", help="Clean up the database after tests")):
    """
    Runs database tests with optimized performance.
    """
    if cleanup:
        sys.argv.append("--cleanup")

    run_tests()


if __name__ == "__main__":
    app()

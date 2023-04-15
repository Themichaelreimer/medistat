import os
import sys
import psycopg2
from multiprocessing import Process

from .common.docker_helpers import get_docker_containers_by_name

"""
    Initializes the database. If a database already exists, it may be dropped and recreated, so that it can be rebuild cleanly.
"""

EXPECTED_DATABASE_CONTAINER_NAME = "postgres"
EXPECTED_BACKEND_CONTAINER_NAME = "backend"
CONNECTION_TIMEOUT = 10


def run() -> None:
    # If -y is supplied, then we assume the user definitely knows what they're doing here
    # Useful to supply, for github actions
    if not "-y" in sys.argv:
        print(
            f"You are about to initialize your local database running with docker. If you have any existing data, it will be lost forever (a long time)."
        )
        if input("Do you want to continue? (Y/n)") != "Y":
            print("Command cancelled")
            exit(0)

    dbname = os.environ.get("DATABASE_NAME")
    hostname = "db." + os.environ.get("HOST", "localhost")
    postgres_user = os.environ.get("POSTGRES_USERNAME")
    postgres_pass = os.environ.get("POSTGRES_PASSWORD")

    # Used to drop and re-create using .env file
    database_container_ids = get_docker_containers_by_name(EXPECTED_DATABASE_CONTAINER_NAME, filter_by_project_name=True)
    assert len(database_container_ids) == 1, f"There should be exactly one database container. Found {database_container_ids}"
    database_container_id = database_container_ids[0].id

    # Used to run migrations after re-creating the DB
    backend_container_ids = get_docker_containers_by_name(EXPECTED_BACKEND_CONTAINER_NAME, filter_by_project_name=True)
    assert len(backend_container_ids) == 1, f"There should be exactly one backend container. Found {backend_container_ids}"
    backend_container_id = backend_container_ids[0].id

    print("Dropping existing database...")
    os.system(f'docker exec {database_container_id} bash -c "su postgres && dropdb -U {postgres_user} --if-exists {dbname}"')

    print("Creating new database...")
    os.system(f'docker exec {database_container_id} bash -c "su postgres && createdb -U {postgres_user} {dbname} --password {postgres_pass}"')

    print("Running migrations...")
    os.system(f'docker exec {backend_container_id} bash -c "source venv-backend/bin/activate && python3 manage.py migrate"')

    print("Testing connection...")

    test_process = Process(target=test_db_connection, name="test_db_connection")
    test_process.start()
    test_process.join(timeout=CONNECTION_TIMEOUT)
    test_process.terminate()

    if test_process.exitcode is None:
        print(f"Could not connect to database at {hostname}: connection timeout.")
        exit(1)
    elif test_process.exitcode == 0:
        print("Connection successful!")
    else:
        print("Connection failed")

    if "--sample-data" in sys.argv or "-D" in sys.argv:
        print("Importing sample data...")
        os.system(
            f'docker exec {backend_container_id} bash -c "source venv-backend/bin/activate && python3 manage.py loaddata sample_data.json"'
        )

    print("Done")


def test_db_connection() -> None:
    dbname = os.environ.get("DATABASE_NAME")
    hostname = "db." + os.environ.get("HOST", "localhost")
    postgres_user = os.environ.get("POSTGRES_USERNAME")
    postgres_pass = os.environ.get("POSTGRES_PASSWORD")

    try:
        conn = psycopg2.connect(dbname=dbname, host=hostname, user=postgres_user, password=postgres_pass)
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")
        exit(1)

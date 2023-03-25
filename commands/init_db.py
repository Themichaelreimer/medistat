import os
import sys

from .common.docker_helpers import get_docker_container_ids_by_name, bash

"""
    Initializes the database. If a database already exists, it may be dropped and recreated, so that it can be rebuild cleanly.
"""

EXPECTED_DATABASE_CONTAINER_NAME = "postgres"
EXPECTED_BACKEND_CONTAINER_NAME = "backend"


def run():
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
    postgres_user = os.environ.get("POSTGRES_USERNAME")

    # Used to drop and re-create using .env file
    database_container_ids = get_docker_container_ids_by_name(EXPECTED_DATABASE_CONTAINER_NAME)
    assert len(database_container_ids) == 1, f"There should be exactly one database container ID. Found {database_container_ids}"
    database_container_id = database_container_ids[0]

    # Used to run migrations after re-creating the DB
    backend_container_ids = get_docker_container_ids_by_name(EXPECTED_BACKEND_CONTAINER_NAME)
    assert len(backend_container_ids) == 1, f"There should be exactly one backend container ID. Found {backend_container_ids}"
    backend_container_id = backend_container_ids[0]

    print("Dropping existing database...")
    os.system(f'docker exec {database_container_id} bash -c "su postgres && dropdb -U {postgres_user} --if-exists {dbname}"')

    print("Creating new database...")
    os.system(f'docker exec {database_container_id} bash -c "su postgres && createdb -U {postgres_user} {dbname}"')

    print("Running migrations...")
    os.system(f'docker exec {backend_container_id} bash -c "source venv-backend/bin/activate && python3 manage.py migrate"')

    print("Done")

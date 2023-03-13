import os, sys
import docker

"""
    This implements a command that acts as a proxy for the manage.py inside the existing container.
    It is useful for things like:
        - Runnning tests inside an image
        - Running migrations in production
        - collecting static assets
        - Easily accessing the django shell

    Example:
    >>> python3 manager.py manage shell
    >>> python3 manager.py manage migrate
"""


EXPECTED_CONTAINER_NAME='backend'

def run():
    args = sys.argv[1:]
    load_venv = "source venv-backend/bin/activate"
    cmd = f'python3 manage.py {" ".join(args)}'
    container_id = get_backend_container_id()
    os.system(f'docker exec {container_id} /bin/bash -c "{load_venv} && {cmd}"')

def get_backend_container_id() -> str:
    docker_interface = docker.from_env()
    containers = docker_interface.containers.list(filters={'name': EXPECTED_CONTAINER_NAME})
    assert len(containers) == 1, f"There should be exactly 1 container with this name. Consider renaming containers. Found: {','.join([c.name for c in containers])}"
    return containers[0].id
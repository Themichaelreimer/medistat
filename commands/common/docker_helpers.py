import os
import docker
from typing import List

def bash(cmd:str) -> int:
    """
        Executes a command through bash. Essentially a wrapper around `os.system(f'bash -c "{cmd}"')
    """

def detect_docker_compose_command() -> str:
    """
        Returns the name of the docker compose command installed on the system.
        (If standalone, it will be `docker-compose`, else `docker compose``).

        Throws an error otherwise
    """

    if os.system('docker-compose --version') == 0:
        return 'docker-compose'
    if os.system('docker compose --version') == 0:
        return 'docker compose'
    else:
        raise Exception("Could not find docker compose. Are you sure it's installed?")

def get_docker_container_ids_by_name(name:str) -> List[str]:
    """
        Returns the ids of the containers that contain `name` as a substring.
        :param name: All containers returned will have `name` as a substring
        :return: list of string ids of dockercontainers
    """
    docker_interface = docker.from_env()
    containers = docker_interface.containers.list(filters={'name': name})
    return [x.id for x in containers]

def ensure_env_file_exists():
    """
        Ensures the .env file exists at the appropriate path.
        If the file already exists, this function does nothing.
        If the file doesn't exist, the sample .env file is moved to the expected path.
    """
    if not '.env' in os.listdir():
        os.system("bash -c 'cp config/sample.env .env'")
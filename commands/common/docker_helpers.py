import os
import docker
import subprocess
import re
from typing import List, Dict

# The traefik container is managed seperately from docker-compose, because we have multiple copies of
# our docker-compose stack running on the same server, but there needs to be no more than 1 traefik instance
TRAEFIK_CONTAINER_NAME = "traefik"


def bash(cmd: str) -> int:
    """
    Executes a command through bash. Essentially a wrapper around `os.system(f'bash -c "{cmd}"')
    The main use of this is for making the project cross platform. Running the project on windows requires some
    implementation of bash on the path
    """
    return os.system(f'bash -c "{cmd}"')


def get_docker_project_name() -> str:
    """
    Returns the docker project name. This string is used as a prefix to all container names
    """
    return os.environ.get("PROJECT_NAME", "medistat")


def detect_docker_compose_command() -> str:
    """
    Returns the name of the docker compose command installed on the system.
    (If standalone, it will be `docker-compose`, else `docker compose``).

    Throws an error otherwise
    """

    if bash("docker-compose --version") == 0:
        return "docker-compose"
    if bash("docker compose --version") == 0:
        return "docker compose"
    else:
        raise Exception("Could not find docker compose. Are you sure it's installed?")


def get_docker_compose_version() -> str:
    """
    Returns the version of docker-compose being used. eg: "2.15" or "1.29.2"
    """
    docker_compose = detect_docker_compose_command()
    command_tokens = docker_compose.split() + ["--version"]
    version_output = subprocess.run(command_tokens, stdout=subprocess.PIPE).stdout.decode()

    matches = re.search(r"\d[\d\/.]*", version_output)
    if matches:
        return matches[0]
    raise Exception(f"Could not parse output of {''.join(command_tokens)}: {version_output}")


def get_docker_containers_by_name(name: str, filter_by_project_name: bool = True) -> List[str]:
    """
    Returns the containers that contain `name` as a substring.
    :param name: All containers returned will have `name` as a substring
    :param filter_by_project_name: Whether to only show containers with the PROJECT_NAME used in your .env file
    :return: list of docker container objects
    """
    project_name = get_docker_project_name()
    cli = docker.from_env()

    # list will only allow us to filter by one condition at a time, but we need two.
    containers = cli.containers.list(filters={"name": name})
    if filter_by_project_name:
        return [x for x in containers if re.match(f"{project_name}[_-]{name}[_-]\d", x.name)]
    return [x for x in containers]


def ensure_env_file_exists():
    """
    Ensures the .env file exists at the appropriate path.
    If the file already exists, this function does nothing.
    If the file doesn't exist, the sample .env file is moved to the expected path.
    """
    if not ".env" in os.listdir():
        bash("cp config/sample.env .env")


def get_containers_map(filter_by_project_name: bool = True) -> Dict[str, docker.models.containers.Container]:
    """
    Returns a dict mapping container_name -> container object
    :param filter_by_project_name: Whether to only consider containers with the project name currently defined
    in your .env file. Default is True
    :return: A dict mapping container_name -> container_object
    """
    project_name = get_docker_project_name()
    cli = docker.from_env()

    filters = {"name": project_name} if filter_by_project_name else {}

    containers = cli.containers.list(filters=filters)
    return {x.name: x for x in containers}

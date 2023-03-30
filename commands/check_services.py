from docker.models.containers import Container  # Only imported for type hinting
from typing import Optional
import yaml
from time import sleep

from .common.docker_helpers import (
    get_containers_map,
    get_docker_containers_by_name,
    get_docker_compose_version,
    get_docker_project_name,
)

"""
    This command checks that all services that should run, are running.

    The main use of this command is in tests, CI/CD pipelines, and monitoring.
    `docker ps` is a better alternative for development purposes
"""

EXPECTED_COMPOSE_FILE_NAMES = ["docker-compose.yml"]
STARTING_MAX_RETRIES = 30  # Retry health check up to this number of times, if the container is still starting
STARTING_RETRY_LATENCY = 5  # Number of seconds between health checks if a container is still starting


def run():
    for COMPOSE_FILE in EXPECTED_COMPOSE_FILE_NAMES:
        compose = get_file_contents(COMPOSE_FILE)
        services = compose["services"]

        # We should be able to find all of these in a 'Running' state
        service_names = list(services.keys())
        is_docker_compose_v1 = get_docker_compose_version()[0] == "1"
        project_name = get_docker_project_name()

        containers = get_containers_map()
        for service in service_names:
            expected_container_name = f"{project_name}_{service}_1" if is_docker_compose_v1 else f"{project_name}-{service}-1"
            assert expected_container_name in containers, f"Container `{expected_container_name}` is not running"

            container = containers[expected_container_name]
            check_container_state(container)

    # The reverse proxy might not be running on this stack - it's "universal", so that one container services all stacks
    reverse_proxy = get_docker_containers_by_name("reverse-proxy")
    assert len(reverse_proxy) == 1, "There should be exactly one container named `reverse-proxy`"
    reverse_proxy = reverse_proxy[0]
    check_container_state(reverse_proxy)

    print("All services are running and healthy!")


def get_file_contents(compose_file_name: str) -> dict:
    """
    Returns the docker compose file contents as a dict
    :param compose_file_name: file name of docker compose file. Must be relative to project root
    :return: file contents as dict
    """
    with open(compose_file_name) as file:
        return yaml.load(file, Loader=yaml.CLoader)


def check_container_state(container: Container) -> None:
    """
    Checks the state of a container to tell whether it's healthy and running.
    Raises an exception if this is not the case, with a useful error message
    """
    status = container.attrs["State"]["Status"]
    assert status == "running", f"Container `{container.name}` has status `{status}`. It should be `running`."

    # health_state only present if health check is defined, else is None
    for _ in range(STARTING_MAX_RETRIES):
        health_state = get_container_health_state(container)
        if health_state:
            if health_state == "healthy":
                return
            elif health_state == "unhealthy":
                raise Exception(f"Container `{container.name}` has health status of `{health_state}`. It should be `healthy`.")
            elif health_state == "starting":
                # Note that this is the only condition that allows the loop to reach the next iteration
                print(f"Container `{container.name}` is still starting. Waiting {STARTING_RETRY_LATENCY}s")
                sleep(STARTING_RETRY_LATENCY)
                # Need to refresh our container object to get the new object state, else it'll be healthy and we'll never know
                container = get_containers_map()[container.name]
            else:
                raise Exception(f"Unexpected container health state: {health_state}")
        else:
            # No health state
            return
    raise Exception("Max 'starting' retries reached. Consider investigating why the container is starting slowly, or adjust retry parameters.")


def get_container_health_state(container: Container) -> Optional[str]:
    """
    Returns the health state of the container.
    None will be returned if the container does not define a health check

    Expected values are in: ['healthy', 'unhealthy', 'starting', None]
    :param container: Docker container object
    :return: One of ['healthy', 'unhealthy', 'starting', None]
    """
    if "Health" in container.attrs["State"]:
        return container.attrs["State"]["Health"]["Status"]
    return None

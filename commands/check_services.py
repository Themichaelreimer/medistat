from docker.models.containers import Container  # Only imported for type hinting
import yaml

from .common.docker_helpers import get_containers_map

"""
    This command checks that all services that should run, are running.

    The main use of this command is in tests, CI/CD pipelines, and monitoring.
    `docker ps` is a better alternative for development purposes
"""

EXPECTED_COMPOSE_FILE_NAME = 'docker-compose.yml'

def run():
    compose = get_file_contents()
    services = compose['services']

    # We should be able to find all of these in a 'Running' state
    service_names = list(services.keys())

    containers = get_containers_map()
    for service in service_names:
        expected_container_name = f"medistat_{service}_1"
        assert expected_container_name in containers, f'Container `{expected_container_name}` is not running'

        container = containers[expected_container_name]
        check_container_state(container)

    print("All services are running and healthy!")

def get_file_contents() -> dict:
    with open(EXPECTED_COMPOSE_FILE_NAME) as file:
        return yaml.load(file, Loader=yaml.CLoader)
    

def check_container_state(container:Container) -> None:
    """
        Checks the state of a container to tell whether it's healthy and running.
        Raises an exception if this is not the case, with a useful error message
    """
    status = container.attrs['State']['Status']
    assert status == 'running', f'Container `{container.name}` has status `{status}`. It should be `running`.'

    # Health only present if health check is defined
    if 'Health' in container.attrs['State']:
        health = container.attrs['State']['Health']['Status']
        assert health == 'healthy', f'Container `{container.name}` has health status of `{health}`. It should be `healthy`.'
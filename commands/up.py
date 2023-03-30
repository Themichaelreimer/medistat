import os
from .common.docker_helpers import (
    detect_docker_compose_command,
    ensure_env_file_exists,
    get_docker_project_name,
    get_docker_containers_by_name,
    TRAEFIK_CONTAINER_NAME,
)


def run():
    ensure_env_file_exists()
    command = detect_docker_compose_command()
    project_name = get_docker_project_name()

    # Main stack
    os.system(f'bash -c "{command} -f docker-compose.yml -p {project_name} up -d"')

    # Traefik reverse proxy
    if not get_docker_containers_by_name("traefik", filter_by_project_name=False):
        os.system(f'bash -c "{command} -f docker-compose-traefik.yml -p {project_name} up -d"')

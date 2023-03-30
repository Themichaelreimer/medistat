import os
from .common.docker_helpers import detect_docker_compose_command, get_docker_project_name, get_docker_container_ids_by_name, TRAEFIK_CONTAINER_NAME


def run():
    command = detect_docker_compose_command()
    project_name = get_docker_project_name()

    # Traefik reverse proxy - need to only have one copy on one machine, that gets used by all copies of the stack
    if get_docker_container_ids_by_name('traefik'):
        os.system(f'bash -c "{command} -f docker-compose-traefik.yml -p {project_name} down"')

    # Main stack
    os.system(f'bash -c "{command} -f docker-compose.yml -p {project_name} down"')

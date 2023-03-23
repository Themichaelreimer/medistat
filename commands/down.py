import os
from .common.docker_helpers import detect_docker_compose_command, get_docker_project_name

def run():
    command = detect_docker_compose_command()
    project_name = get_docker_project_name()

    os.system(f'bash -c "{command} -p {project_name} down"')



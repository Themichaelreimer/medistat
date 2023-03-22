import os
from .common.docker_helpers import detect_docker_compose_command, ensure_env_file_exists, get_docker_project_name

def run():
    ensure_env_file_exists()
    command = detect_docker_compose_command()
    project_name = get_docker_project_name()
    os.system(f'bash -c "{command} -p {project_name} up -d"')

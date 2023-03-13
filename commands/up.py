import os
from .common.docker_helpers import detect_docker_compose_command, ensure_env_file_exists

def run():
    ensure_env_file_exists()
    command = detect_docker_compose_command()
    os.system(f'bash -c "{command} up -d"')

import os, sys
from .common.docker_helpers import (
    detect_docker_compose_command,
    ensure_env_file_exists,
    get_docker_project_name,
    get_network,
    create_network,
    REVERSE_PROXY_NETWORK_NAME,
)


def run():
    ensure_env_file_exists()
    command = detect_docker_compose_command()
    project_name = get_docker_project_name()

    # TODO: Consider if this is a systemd service
    daemon_flag = "-d" if not ("--terminal" in sys.argv or "-t" in sys.argv) else ""

    # Main stack
    os.system(f'bash -c "{command} -f docker-compose.yml -p {project_name} up -d"')

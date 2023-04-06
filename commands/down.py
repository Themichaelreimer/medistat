import os, sys
from .common.docker_helpers import (
    detect_docker_compose_command,
    get_docker_project_name,
)


def run() -> None:
    command = detect_docker_compose_command()
    project_name = get_docker_project_name()

    # TODO: Consider if this is a systemd service
    daemon_flag = "-d" if not ("--terminal" in sys.argv or "-t" in sys.argv) else ""

    # Main stack
    os.system(f'bash -c "{command} -f docker-compose.yml -p {project_name} down"')

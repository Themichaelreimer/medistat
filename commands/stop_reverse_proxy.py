import os, sys
import docker

from .common.docker_helpers import (
    detect_docker_compose_command,
)


def run() -> None:
    command = detect_docker_compose_command()

    # TODO: Consider if this is a systemd service
    daemon_flag = "-d" if not ("--terminal" in sys.argv or "-t" in sys.argv) else ""
    os.system(f'bash -c "{command} -f docker-compose-traefik.yml -p reverse_proxy down"')

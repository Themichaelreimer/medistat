import os, sys

from .common.docker_helpers import detect_docker_compose_command


def run():
    command = detect_docker_compose_command()
    use_ssl = os.environ.get('SSL') == 'true'
    file = 'docker-compose-traefik-ssl.yml' if use_ssl else 'docker-compose-traefik.yml'

    # TODO: Consider if this is a systemd service
    daemon_flag = "-d" if not ("--terminal" in sys.argv or "-t" in sys.argv) else ""
    os.system(f'bash -c "{command} -f {file} -p reverse_proxy up {daemon_flag}"')

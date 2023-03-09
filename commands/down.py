import os
from .common.docker_helpers import detect_docker_compose_command

def run():
    command = detect_docker_compose_command()
    os.system(f'bash -c "{command} down"')



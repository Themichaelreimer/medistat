import os

def detect_docker_compose_command() -> str:
    """
        Returns the name of the docker compose command installed on the system.
        (If standalone, it will be `docker-compose`, else `docker compose``).

        Throws an error otherwise
    """

    if os.system('docker-compose --version') == 0:
        return 'docker-compose'
    if os.system('docker compose --version') == 0:
        return 'docker compose'
    else:
        raise Exception("Could not find docker compose. Are you sure it's installed?")
    
def ensure_env_file_exists():
    """
        Ensures the .env file exists at the appropriate path.
        If the file already exists, this function does nothing.
        If the file doesn't exist, the sample .env file is moved to the expected path.
    """
    if not '.env' in os.listdir():
        os.system("bash -c 'cp config/sample.env .env'")
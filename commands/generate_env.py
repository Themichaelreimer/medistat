import os, sys

"""
    This command generates an env file for a PR deployment, based on the name of the PR (Should be something like: PR102)
"""

SAMPLE_ENV_PATH = "config/sample.env"
EXPECTED_PRODUCTION_HOST = "medistat.online"


def run() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 manager.py generate_env <PR_NAME>")
        exit(1)

    pr_name = sys.argv[1].lower()
    sample_env = read_sample_env_file()
    sample_env = replace_host(sample_env, pr_name)
    sample_env = replace_frontend_host(sample_env, pr_name)
    sample_env = replace_project_name(sample_env, pr_name)
    sample_env = replace_ssl_status(sample_env)

    write_env_file(sample_env)


def read_sample_env_file() -> str:
    """
    Reads the sample env file into a string.
    Our env file is going to use this as a base, and edit a few values.
    """
    with open(SAMPLE_ENV_PATH, "r") as sample_env:
        contents = sample_env.read()
        return contents


def write_env_file(file_contents: str) -> None:
    with open(".env", "w") as env_file:
        env_file.write(file_contents)


def replace_host(env_file_contents: str, pr_name: str) -> str:
    return env_file_contents.replace("HOST=localhost", f"HOST=medistat.online")


def replace_frontend_host(env_file_contents: str, pr_name: str) -> str:
    return env_file_contents.replace("FRONTEND_HOST=medistat.online", f"FRONTEND_HOST={pr_name}.medistat.online")


def replace_project_name(env_file_contents: str, pr_name: str) -> str:
    return env_file_contents.replace("PROJECT_NAME=medistat_dev", f"PROJECT_NAME=medistat_{pr_name}")


def replace_ssl_status(env_file_contents: str) -> str:
    return env_file_contents.replace("SSL=false", "SSL=true")

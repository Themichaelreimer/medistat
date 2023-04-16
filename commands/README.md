# Commands

This folder contains the project's management commands. These commands are run via:

    python3 manager.py [COMMAND_NAME]

where `COMMAND_NAME` is the name of a file in this directory ending in `.py`, without the `.py`. For example, the following runs the `run()` function of `build.py`:

    python3 manager.py build

# List
|Command Name|Description|Example|
|------------|-----------|-------|
|`build`|Builds the necessary custom docker images for deployment| `python3 manager.py build`|
|`check_code_quality`|Checks `mypy` and `black` for code smells. This will usually also be done by pre-commit hooks and VSCode extensions, but this command enforces the checks in the github actions checks.| `python3 manager.py check_code_quality`|
|`check_services`| Checks that all docker services are healthy. If a service is still starting, the check will be retried a number of times before the command fails. Used as part of a regular status check in status checks and monitoring. | `python3 manager.py check_services`|
|`down`| Brings down all docker services **that match the project name listed in your `.env` file**| `python3 manager.py down`|
|`flush_cache`| Flushes the redis cache of the current stack. | `python3 manager.py flush_cache`|
|`help`|Lists all availble `manager.py` commands|`python3 manager.py` or `python3 manager.py help`|
|`init_db`|Recreates the postgres DB state using the credentials listed in your `.env` file. If a database already exists, it will be deleted first. (There is a confirmation check in this command)| `python3 manager.py init_db`|
|`generate_env`| Generates an appropriate .env file for a stack based on a PR name. The only intended use of this command is for automatic deployment of Pull Requests to subdomains for easy review |
|`manage`|A Proxy to the backend's Django `manage.py`. Useful for running migrations, tests, etc inside the container, without the use of `docker exec -it ...`| `python3 manager.py manage migrate`|
|`start_reverse_proxy`|Starts the global `traefik` instance. No services will be exposed to the internet without this command. Note that there should only be one instance of this container **per machine**, even if multiple stacks are running on that machine.| `python3 manager.py start_reverse_proxy`|
|`stop_reverse_proxy`|Stops the global `traefik` instance.|`python3 manager.py stop_reverse_proxy`|
|`up`|Brings up all the application services with the project name `{{PROJECT_NAME}}` defined in your .env file. Note that you can deploy multiple copies of the entire project at once, by changing this variable.| `python3 manager.py up`|

# Notes

- Commands must be directly in this folder. Any files in subdirectories can be imported by commands, but cannot be commands themselves.

- To see all available commands in your local environment, run `python3 manager.py help`, or even `python3 manager.py`.

- Commands are imported as requested. That is, `build.py` is dynamically imported when the build command is requested. This prevents issues with one command from possibly being able to affect another one. (eg, syntax errors)

- Commands must implement a `run()` function taking no arguments. If arguments are needed, your command should consult `sys.argv` directly.

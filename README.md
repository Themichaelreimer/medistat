# Medistat

This project does stuff with medical statistics, and serves as my
primary portfolio project.

# Table of Contents
- [Getting Started](#getting_started)
    - [Prerequisites](#prerequisites)
    - [Setup](#setup)
- [Repo Components](#repo)
- [Application Services](#services)
- [Developer Experience](#devexp)
    - [Github Actions](#actions)
    - [Static Typing / MyPy](mypy)
    - [Dependabot](#dependabot)

# Getting Started <a name="getting_started"></a>

## Prerequisites <a name="prerequisites"></a>
The following needs to be installed:
- `docker compose` (Any version should work. Tested with v1 and v2 standalone. Should also work with `docker compose` CLI plugin, but this is not tested.)
- `bash`. Trivial on most systems, but installing is important for Windows users.
- `python` >= 3.5. Needed for running management utilities.
- `pip`. Required to install a few packages used by the management utilities.

## Setup<a name="setup"></a>

I have taken great care to ensure this project is as easy to get started with as humanly possible.

- Ensure prerequisites are installed.
- Install management packages via `pip3 install -r requirements.txt`
- `python3 manager.py build` to build docker images for the frontend and backend.
- `python3 manager.py up` to start the services. `python3 manager.py down` can be used later to shut them down.
- `python3 manager.py init_db` to (re)build the database, including running all migrations. If it already exists, it will be dropped, recreated, and migrated.

## Manager Commands

[See README in commands folder](commands/README.md) for a complete list of commands and their descriptions

# Repo Components Tour <a name="repo"></a>

This section contains a description of all the major folders in the root of the repo.
|Folder | Description|
|-------|------------|
|backend|This folder contains the Django project that implements the project backend.|
|frontend|This folder contains the Vue project that implements the project frontend.|
|commands|This folder contains various stack management commands that can be run via `manager.py`|
|config|This folder contains various static config files, including systemd service files and a sample `.env` file|

# Application Services <a name="services"></a>
|Service|Description|
|-------|-----------|
|Backend|This service serves the backend Django project via apache.|
|Frontend|This service serves the frontend Vue project via apache.|
|Postgres 14| Database for Backend|
|Redis|General purpose cache|
|Grafana|Visualization of metrics|


# Developer Experience<a name="devexp"></a>

The following tools and conventions are used to provide the best possible developer experience, and maximize system maintainability

## Github Actions <a name="actions"></a>
GitHub Actions is used for the following purposes on this project:
- Performing CI checks to enforce various code quality metrics and conditions (eg, tests passing, linting, static analysis)
- Ensuring builds are easily repeatable and correctly automated
- Continuous updating of production as `main` gets updated
- Automatically and continously deploying successful builds of open pull requests to https://pr{{PR NUMBER HERE}}.medistat.online
    - Link to the deployed branch-under-review is automatically posted as a comment by a bot, when all checks are successful
    - Deployments for all open PRs get continuously updated until closed
    - Once PRs are merged or closed, their resources are all freed.
## Pre-Commit Hooks
Precommit hooks give a certain level of quality-at-the-source by checking for easy to detect code smells before allowing commits. In most cases, and where possible, the pre-commit hooks will also correct the issues they find.
Precommit hooks are used on this project for:
- Auto-formatting python, yaml, and json files. Checks against large files being commited, trailing whitespace, lines at end of file, tabs, and CLRF.
- Checks that commited python code has a valid AST (ie, no python syntax errors)
- Enforcing static typing according to the mypy configuration
    - Since this was a legacy project that I revived for the sake of demonstrating instrastructure skills, the mypy configuration reflects that of a project that is seeing incremental adoption of static typing. New project areas have stricter rules enforced than older project areas.
- Checks to prevent `breakpoint()` from being commited

## Dependabot <a name="dependabot"></a>
Dependabot is provided by GitHub to check for security concerns in application packages. It automatically opens pull requests that update package versions with security fixes, and those pull requests are automatically tested via the actions pipeline. Note that for many of the security concerns on this project, we're currently stuck with these versions due to incompatibilities between library versions (According to dependabot).

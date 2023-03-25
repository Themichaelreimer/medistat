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

## backend
This folder contains the Django project that implements the project backend.

## frontend
This folder contains the Vue project that implements the project frontend.

## commands
This folder contains various management commands that can be run via `manager.py`

## config
This folder contains various static config files, including systemd service files and a sample `.env` file

# Application Services <a name="services"></a>

## Backend
This service serves the backend Django project via apache.

## Frontend
This service serves the frontend Vue project via apache.

## Redis
General purpose cache

## Grafana
Metrics Visualization

## Postgres
Database

# Developer Experience<a name="devexp"></a>

The following tools and conventions are used to provide the best possible developer experience, and maximize system maintainability

## Github Actions <a name="actions"></a>
GitHub Actions is used for the following purposes on this project:
- Performing CI checks to enforce various code quality metrics and conditions (eg, tests passing, linting, static analysis)
- Ensuring builds are easily repeatable and correctly automated
- Continuous Deployment of the production application
## Static Type-checking / MyPy <a name="mypy"></a>
MyPy is used as part of the checks for code quality, to ensure that where type hints are provided (either by the developer on this project, or by a library), that the code usage doesn't contradict the type hints. In other words, it catches mistakes that are implied by the given type hints, and the better type hints I provide, the more mistakes it can catch early.

Medistat was originally written in 2021, and it did not have any enforcement of type hints at that time. Therefore the configuration of MyPy on this project has gradual adoption in mind, where type hinting can be configured to apply more strictly to some directories than others. See [the config file](config/mypy.ini) for more information

[MyPy has a VSCode plugin that is recommended if you use this IDE.](https://marketplace.visualstudio.com/items?itemName=matangover.mypy)

## Black Code Formatting
Code style is PEP8 as enforced by [black](https://black.readthedocs.io/en/stable/getting_started.html), except with a max line length of 144 instead of 88. Recommended to have black run on save. Checks are enforced via commands/check_code_quality.py 

## Dependabot <a name="dependabot"></a>
Dependabot is provided by GitHub to check for security concerns in application packages. It automatically opens pull requests that
update package versions with security fixes, and those pull requests are automatically tested via the actions pipeline.
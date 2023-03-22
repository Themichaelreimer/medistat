# Medistat

This project does stuff with medical statistics, and serves as my
primary portfolio project.

# Getting Started

## Prerequisites
The following needs to be installed:
- `docker compose` (Any version should work. Tested with v1 and v2 standalone. Should also work with `docker compose` CLI plugin, but this is not tested.)
- `bash`. Trivial on most systems, but installing is important for Windows users.
- `python` >= 3.5. Needed for running management utilities.
- `pip`. Required to install a few packages used by the management utilities.

## Process

I have taken great care to ensure this project is as easy to get started with as humanly possible.

- Ensure prerequisites are installed.
- Install management packages via `pip3 install -r requirements.txt`
- `python3 manager.py build` to build docker images for the frontend and backend.
- `python3 manager.py up` to start the services. `python3 manager.py down` can be used later to shut them down.
- `python3 manager.py init_db` to (re)build the database, including running all migrations. If it already exists, it will be dropped, recreated, and migrated.

## Manager Commands

[See README in commands folder](commands/README.md) for a complete list of commands and their descriptions

# Repo Components Tour

This section contains a description of all the major folders in the root of the repo.

## backend
This folder contains the Django project that implements the project backend.

## frontend
This folder contains the Vue project that implements the project frontend.

## commands
This folder contains various management commands that can be run via `manager.py`

## config
This folder contains various static config files, including systemd service files and a sample `.env` file

# Services Tour

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

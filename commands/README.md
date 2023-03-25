# Commands

This folder contains the project's management commands. These commands are run via:

    python3 manager.py [COMMAND_NAME]

where `COMMAND_NAME` is the name of a file in this directory ending in `.py`, without the `.py`. For example, the following runs the `run()` function of `build.py`:

    python3 manager.py build

# Notes

- Commands must be directly in this folder. Any files in subdirectories can be imported by commands, but cannot be commands themselves.

- To see all available commands in your local environment, run `python3 manager.py help`, or even `python3 manager.py`.

- Commands are imported as requested. That is, `build.py` is dynamically imported when the build command is requested. 

- Commands must implement a `run()` function taking no arguments. If arguments are needed, your command should consult `sys.argv` directly.
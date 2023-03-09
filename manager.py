"""
    This script acts as a management interface for the entire project.
    
    Commands are defined in the commands/ folder. Each command is it's own python file that defines a `run` function.
    The name of the command comes from the name of the file, and is called by:

    >>> python3 manager.py command_name <ARGS?>

    If any kind of argparse is wanted, that should be implemented inside each command.
"""

import sys
import importlib

if __name__ == "__main__":
    
    print(f'{sys.argv=}')
    command = None
    try:
        command = sys.argv[1]
    except:
        module = importlib.import_module(f'commands.help')
        module.run()
        exit(127)

    if command:
        try:
            sys.argv = sys.argv[1:]  # Effectively removes the manager.py from sys.argv. Makes things easier for argparse 
            module = importlib.import_module(f'commands.{command}')
            module.run()
        except ModuleNotFoundError as e:
            print(e)
            print(f"Could not find command {command} in commands folder")


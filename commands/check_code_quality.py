import os

def run():
    # Something important that needs to be done, that this hides:
    # mypy won't work correctly without environment variables being loaded.
    # Running through manager.py loads the .env file behind the scenes.
    status_code = os.system("mypy . --explicit-package-bases --config-file config/mypy.ini")
    exit(os.WEXITSTATUS(status_code))
import os


def run():
    # Something important that needs to be done, that this hides:
    # mypy won't work correctly without environment variables being loaded.
    # Running through manager.py loads the .env file behind the scenes.

    # mypy (type checking)
    status_code = os.system("mypy . --explicit-package-bases --config-file config/mypy.ini")
    if status_code:
        # No hint necessary: above command will have outputted recommendations
        exit(os.WEXITSTATUS(status_code))

    # black (code formatting, should usually be redundant if all else is set up correctly)
    status_code = os.system("black . --config=config/black.cfg --check")
    if status_code:
        print(
            "HINT: Is black installed? If you run `black . --config-config/black.cfg`, it will reformat your project in a way that passes the checks."
        )
        exit(os.WEXITSTATUS(status_code))

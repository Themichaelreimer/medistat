import os
import sys
from .common.docker_helpers import bash


def run() -> None:
    export = ""
    if sys.platform == "darwin":
        # In this case, we will force the use of x86_64 images, even though
        # if we are on apple sillicon this may introduce a performance hit.
        #
        # This is done because the ARM versions of many images are frequently broken
        # and it is more important to get consistent, reliable builds
        # than to have better performance and deal with failures regularly
        export = "export DOCKER_DEFAULT_PLATFORM=linux/amd64 &&"

    # TODO: Non-recursively walk through folders in root folder; check them for docker files. Build command if found
    bash(f"{export} docker build . --file backend/Dockerfile -t backend")
    bash(f"{export} docker build . --file frontend/Dockerfile -t frontend")
    print("hi")

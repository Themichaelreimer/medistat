import os

def run():
    # TODO: Non-recursively walk through folders in root folder; check them for docker files. Build command if found
    os.system('docker build . --file backend/Dockerfile -t backend')
    os.system('docker build . --file frontend/Dockerfile -t frontend')

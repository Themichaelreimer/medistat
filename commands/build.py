import os

def run():
    os.system('docker build . --file backend/Dockerfile -t backend')

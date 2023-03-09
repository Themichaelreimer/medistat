import os

def run():
    print('Usage: python3 manager.py <COMMAND_NAME> <ARGS?>')

    files = [ x for x in os.listdir('commands') if not os.path.isdir(f'commands/{x}')]
    files.sort()

    print(f'Available commands: ')
    for file in files:
        print(''.join(file.split('.')[:-1]))  # File with out the extension, since the command won't be entered with the extension
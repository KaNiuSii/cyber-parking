import sys
import os
import shutil

def copy_models(source, destination):
    source_path = os.path.join(os.getcwd(), source, 'models')
    destination_path = os.path.join(os.getcwd(), destination, 'models')

    if not os.path.exists(source_path):
        print(f"Error: Source folder '{source_path}' does not exist.")
        sys.exit(1)

    if os.path.exists(destination_path):
        print(f"Destination folder '{destination_path}' already exists. Removing...")
        shutil.rmtree(destination_path)

    print(f"Copying models from '{source_path}' to '{destination_path}'...")
    shutil.copytree(source_path, destination_path)
    print("Copy complete.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python copy_models.py <source> <destination>")
        sys.exit(1)

    source = sys.argv[1]
    destination = sys.argv[2]

    if source not in ['client', 'server'] or destination not in ['client', 'server']:
        print("Error: Arguments must be either 'client' or 'server'.")
        sys.exit(1)

    if source == destination:
        print("Error: Source and destination cannot be the same.")
        sys.exit(1)

    copy_models(source, destination)

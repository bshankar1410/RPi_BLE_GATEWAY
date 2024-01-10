import os
import requests
from zipfile import ZipFile
import io
import hashlib

GITHUB_REPO_URL = "https://github.com/bshankar1410/RPi_BLE_GATEWAY"

CHUNK_SIZE = 1024  # Set your preferred chunk size (in bytes)

sha256 = hashlib.sha256()

def download_file(url, output_path):
    response = requests.get(url)
    response.raise_for_status()
    with open(output_path, 'wb') as f:
        f.write(response.content)

def generate_sha_for_file(file_path):
    with open(file_path, 'rb') as f:
         sha256_object = sha256.new(hash_algorithm)
         while chunk := f.read(CHUNK_SIZE):
               sha256.update(chunk)
    return sha256.hexdigest()

def download_and_verify_github_repo():
    GITHUB_REPO_URL = "https://github.com/bshankar1410/RPi_BLE_GATEWAY"
    output_directory = '/home/pi/RPi_BLE_GAYEWAY/ble-gateway/download_repo'
    try:
        # Get the repository content using GitHub API
        api_url = f"{GITHUB_REPO_URL}/contents/"
        response = requests.get(api_url)
        response.raise_for_status()

        files = response.json()

        for file_info in files:
            # Download all types of files
            file_url = file_info['download_url']
            file_name = os.path.join(output_directory, file_info['path'])
            download_file(file_url, file_name)

            # Generate SHA hash for Python files only
            if file_info['type'] == 'file' and file_name.endswith('.py'):
                sha_file_name = f"{file_name}.sha"
                sha_hash = generate_sha_for_file(file_name)

                # Write SHA hash to a file
                with open(sha_file_name, 'w') as sha_file:
                    sha_file.write(sha_hash)

                print(f"Downloaded and verified: {file_name}")

            # Check if the item is a directory
            elif file_info['type'] == 'dir':
                # Recursively download and verify files in the subdirectory
                subdirectory_url = f"{repo_url}/contents/{file_info['path']}"
                subdirectory_output = os.path.join(output_directory, file_info['name'])
                download_and_verify_github_repo(subdirectory_url, subdirectory_output)

    except Exception as e:
        print(f"An error occurred: {e}")

output_directory = '/home/pi/RPi_BLE_GAYEWAY/ble-gateway/download_repo'

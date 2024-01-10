import os
import requests
import json
import config
import blegateway
import hashlib
import ble2mqtt

CHUNK_SIZE = 1024  # Set your preferred chunk size (in bytes)

sha256 = hashlib.sha256()

GITHUB_RAW_URL = "https://raw.githubusercontent.com/bshankar1410/RPi_BLE_GATEWAY/master/ble-gateway/main.py"
GITHUB_SHA_URL = "https://raw.githubusercontent.com/bshankar1410/RPi_BLE_GATEWAY/master/ble-gateway/main.py.sha"
local_path = "downloaded_ota_file.py"
shafile_path = "downloaded_ota_file.py.sha"
git_shafile_path = "git_shafile.py.sha"

httpCONFIG = config.get_config('http')
header = {'Content-type': 'application/json'}

def heartbeat():
    requests.post(httpCONFIG['host'],
                         data=json.dumps(blegateway.fill_heartbeat()).encode('utf8'),
                         headers=header)

def send_bt(bt_addr, message):
    requests.post(httpCONFIG['host'], data=json.dumps(message).encode('utf8'), headers=header)

def download_ota_file():
    url = GITHUB_RAW_URL
    with requests.get(url, stream=True) as response:
        if response.status_code == 200:
            with open(local_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        file.write(chunk)
            print(f"File downloaded to {local_path}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")


def create_sha_file():
    try:
        with open(local_path, "rb") as file:
            # Read the file in chunks for efficiency
            for byte_block in iter(lambda: file.read(4096), b""):
                sha256.update(byte_block)
        # Save the SHA-256 hash to a file
        with open(shafile_path, 'w') as sha_file:
            sha_file.write(sha256.hexdigest())
    except FileNotFoundError:
        print(f"File not found: {local_path}")
    except Exception as e:
        print(f"Error creating SHA file: {e}")

def download_git_sha_file():
    try:
        # Fetch SHA file content from GitHub
        response = requests.get(GITHUB_SHA_URL)
        response.raise_for_status()
        # Save the SHA file locally
        with open(git_shafile_path, 'w') as sha_file:
            sha_file.write(response.text)
        print(f"SHA file saved locally: {git_shafile_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading SHA file: {e}")

def copy_downloaded_file()
    try:
        with open("downloaded_file.py", 'rb') as source:
            with open("main1.py", 'wb') as destination:
                while chunk := source.read(CHUNK_SIZE):
                    destination.write(chunk)
        print("File contents copied successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

def compare_sha_files()
    sha1 = read_sha_from_file(shafile_path)
    sha2 = read_sha_from_file(git_shafile_path)
    if sha1 is not None and sha2 is not None:
        if sha1 == sha2:
            print("SHA values match. The files are identical.")
            copy_downloaded_file()
        else:
            print("SHA values do not match. The files are different.")
    else:
        print("Error reading SHA files.")

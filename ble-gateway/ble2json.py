import time
import json

bledata_file_path = "/home/pi/RPi_BLE_GATEWAY/ble-gateway/ble_data_file.json"
config_file_path = "/home/pi/RPi_BLE_GATEWAY/ble-gateway/configblegateway.json"
replacement_character = ']'

def remove_contents_from_bledata_file(bledata_file_path):
    try:
        with open(bledata_file_path, "w") as json_file:
            json_file.truncate(0)  # Truncate the file to 0 bytes (remove all contents)
            print(f"Contents of '{bledata_file_path}' have been removed.")
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"Error: {str(e)}")

def is_character_in_bledata_file(bledata_file_path, character):
    try:
        with open(bledata_file_path, "r") as json_file:
            content = json_file.read()
            return character in content
    except FileNotFoundError:
        return False

def append_character_to_bledata_file(bledata_file_path, character):
    with open(bledata_file_path, "a") as json_file:
         json_file.write(character)

# Function to read the last character of a file
def read_last_character_in_bledata_file(bledata_file_path):
    try:
        with open(bledata_file_path, "rb") as json_file:
            json_file.seek(-1, 2)  # Go to the end of the file
            last_character = json_file.read(1).decode('utf-8')
#            print(last_character)
            return last_character
    except FileNotFoundError:
        return None

# Function to replace the last character of a file
def replace_last_character_in_bledata_file(bledata_file_path,):
    try:
        with open(bledata_file_path, "rb+") as json_file:
            json_file.seek(-1, 2)  # Go to the end of the file
            json_file.write(replacement_character.encode('utf-8'))
    except FileNotFoundError:
        print(f"File '{bledata_file_path}' not found.")

# Function to save updated JSON data to a file
def save_config_to_configblegateway_file(config_file_path, json_data):
    try:
        with open(config_file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
        print(f"Updated JSON file: {config_file_path}")
    except Exception as e:
        print(f"Error saving JSON data to file: {str(e)}")

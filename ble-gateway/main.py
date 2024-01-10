import time
import sys
import json
import blegateway
import config
import subprocess
import ble2json
import ble2mqtt
import RPi.GPIO as gpio
import socket
import threading
import generate_shafiles

stop_flag = True
run_flag = True

ble2mqtt.r_led_off()
ble2mqtt.g_led_off()
ble2mqtt.b_led_off()
time.sleep(0.2)
ble2mqtt.r_led_on()

RETRY_INTERVAL = 1

# File Paths
main_path = "main.py"
main_sha_path = "main.py.sha"
ble2http_path = "ble2http.py"
ble2http_sha_path = "ble2http.py.sha"
ble2mqtt_path = "ble2mqtt.py"
ble2mqtt_sha_path = "ble2mqtt.py.sha"
blegateway_path = "blegateway.py"
blegateway_sha_path = "blegateway.py.sha"
config_path = "config.py"
config_sha_path = "config.py.sha"
ble2json_path = "ble2json.py"
ble2json_sha_path = "ble2json.py.sha"

generate_shafiles.create_sha_file(main_path,main_sha_path)
generate_shafiles.create_sha_file(ble2http_path,ble2http_sha_path)
generate_shafiles.create_sha_file(ble2mqtt_path,ble2mqtt_sha_path)
generate_shafiles.create_sha_file(blegateway_path,blegateway_sha_path)
generate_shafiles.create_sha_file(config_path,config_sha_path)
generate_shafiles.create_sha_file(ble2json_path,ble2json_sha_path)

anusha="Hi anusha"

character_to_check = '['

subprocess.run(['sudo', 'service', 'bluetooth', 'start'], check=True)

if config.get_config('bleDevice')['bleDevice'] == 1:
    # Import Receiver for nRF module
    from beaconscanner import BeaconReceiver
    print("BLE nRF Module")
else:
    # Import bluez scanner
    from beaconscanner import BeaconScanner
    print("Pi inbuilt BLE")

mqttEnabled = config.get_config('endpoints')['mqttEnabled']
httpEnabled = config.get_config('endpoints')['httpEnabled']

blescantime = config.get_config('optime')['scantime']
blepushtime = config.get_config('optime')['pushtime']

if mqttEnabled:
    import ble2mqtt
if httpEnabled:
    import ble2http


try:
    names = config.get_config('names')
except:
    namesEnabled = False
else:
    namesEnabled = True

mFen = config.get_config('filters')['macFilterEnabled']
if mFen:
    mF = config.get_config('filters')['macFilter']


ble2json.remove_contents_from_bledata_file(ble2json.bledata_file_path)
if not ble2json.is_character_in_bledata_file(ble2json.bledata_file_path, character_to_check):
       ble2json.append_character_to_bledata_file(ble2json.bledata_file_path, character_to_check)
       print(f"Appended '{character_to_check}' to the JSON file.")
else:
       print(f"'{character_to_check}' is already in the JSON file.")


def watchdog_timer(timeout_seconds):
    global run_flag
    time.sleep(timeout_seconds)
    if run_flag==False:
        print("Program has stopped responding. Restarting the Raspberry Pi...")
        subprocess.run(["sudo", "reboot"])


def callback(bt_addr, rssi, packet, dec, smoothedRSSI):
    global stop_flag
    if stop_flag:
        if namesEnabled:
            if bt_addr in names:
                name = names[bt_addr]
            else:
                name = None
        else:
            name = None
        if mFen == True:
            for i in mF:
                if str.upper(i) == bt_addr:
                   print("Storing BLE data in file111...")
                   if not ble2json.is_character_in_bledata_file(ble2json.bledata_file_path, character_to_check):
                       ble2json.append_character_to_bledata_file(ble2json.bledata_file_path, character_to_check)
                       print(f"Appended '{character_to_check}' to the JSON file.")
                   else:
                       print(f"'{character_to_check}' is already in the JSON file.")
                   with open(ble2json.bledata_file_path, "a") as json_file:
                       message = blegateway.ble_message(bt_addr, rssi, packet, dec, smoothedRSSI, name)
                       #print("File data to write:",message)
                       json.dump(message, json_file, indent=4)
                       json_file.write(',')
                       json_file.close()
        else:
                   print("Storing BLE data in file...")
                   last_character = ble2json.read_last_character_in_bledata_file(ble2json.bledata_file_path)
                   if last_character != ']':
                      with open(ble2json.bledata_file_path, "a") as json_file:
                           message = blegateway.ble_message(bt_addr, rssi, packet, dec, smoothedRSSI, name)
                           #print("File data to write:",message)
                           json.dump(message, json_file, indent=4)
                           json_file.write(',')
                           json_file.close()
    else:
        print("File ready to upload")

def check_connectivity(host="8.8.8.8", port=53, timeout=5):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        return False

def retry_connection():
    while True:
        print("Attempting to establish a connection...")
        if check_connectivity():
            print("Internet connection established.")
            ble2json.remove_contents_from_bledata_file(ble2json.bledata_file_path)
            if not ble2json.is_character_in_bledata_file(ble2json.bledata_file_path, character_to_check):
                   ble2json.append_character_to_bledata_file(ble2json.bledata_file_path, character_to_check)
                   print(f"Appended '{character_to_check}' to the JSON file.")
            else:
                   print(f"'{character_to_check}' is already in the JSON file.")
                       #subprocess.run(['sudo', 'service', 'bluetooth', 'start'], check=True)
            return True
        else:
            print(f"Connection attempt failed. Retrying in {RETRY_INTERVAL} seconds...")
            ble2mqtt.g_led_blink()
            time.sleep(RETRY_INTERVAL)

def main_loop():
    global stop_flag
    global run_flag
    try:
       count=0
       if check_connectivity():
           print("Internet is connected. Proceeding with the next steps.")
           ble2mqtt.g_led_on()
           RSSIen = config.get_config('filters')['rssiThreshold']
           if (RSSIen):
               RSSI = config.get_config('filters')['rssi']
           else:
               RSSI = -999
           if mqttEnabled:
               ble2mqtt.MQTT()
           if httpEnabled:
               ble2mqtt.HTTP()
           global scanner
           f = config.get_config('filters')
           if config.get_config('bleDevice')['bleDevice'] == 1:
               scanner = BeaconReceiver(callback, config.get_config('bleDevice')['serialPort'], \
                                config.get_config('bleDevice')['baudrate'], \
                                config.get_config('bleDevice')['timeout'],\
                                rssiThreshold=RSSI,\
                                ruuvi=f['ruuvi'], ruuviPlus=f['ruuviPlus'], \
                                eddystone=f['eddystone'], ibeacon=f['ibeacon'], unknown=f['unknown'])
           else:
               scanner = BeaconScanner(callback, rssiThreshold=RSSI,\
                                ruuvi=f['ruuvi'], ruuviPlus=f['ruuviPlus'], \
                                eddystone=f['eddystone'], ibeacon=f['ibeacon'], unknown=f['unknown'])
           scanner.start()
           stop_flag = True
           scanner._mon.toggle_scan(True)
           ble2mqtt.receive_config()
           while True:
               if check_connectivity()==False:
                   scanner._mon.toggle_scan(False)
                   ble2mqtt.b_led_off()
                   ble2mqtt.g_led_off()
                   main_loop()
               else:
                   ble2mqtt.b_led_on()
                   ble2mqtt.g_led_on()
               if config.get_config('bleDevice')['bleDevice'] == 1:
                   time.sleep(blepushtime)
                   if mqttEnabled:
                       ble2mqtt.heartbeat()
                   if httpEnabled:
                       ble2http.heartbeat()
               else:
                   #subprocess.run(['sudo', 'service', 'bluetooth', 'stop'], check=True)
                   count = count+1
                   print("count=",count)
                   print("BlePushTime:", blepushtime)
                   time.sleep(blepushtime)
                   stop_flag=False
                   scanner._mon.toggle_scan(False)
#                  stop_Flag = False
                   print("Sending gateway & BLEdata...")
                   last_character = ble2json.read_last_character_in_bledata_file(ble2json.bledata_file_path)
                   if last_character is not None and last_character != ']':
                          ble2json.replace_last_character_in_bledata_file(ble2json.bledata_file_path)
                          print(f"Replaced last character with '{ble2json.replacement_character}' in the JSON file.")
                   else:
                            print("The last character is either None or already ']'.")
                   scanner._mon.toggle_scan(False)
                   try:
                       with open(ble2json.bledata_file_path, "r") as json_file:
                            data=json.load(json_file)
                   except Exception as e:
                           print(f"An error occurred: {str(e)}")
                           ble2json.remove_contents_from_bledata_file(ble2json.bledata_file_path)
                           if not ble2json.is_character_in_bledata_file(ble2json.bledata_file_path, character_to_check):
                                  ble2json.append_character_to_bledata_file(ble2json.bledata_file_path, character_to_check)
                                  print(f"Appended '{character_to_check}' to the JSON file.")
                           else:
                                  print(f"'{character_to_check}' is already in the JSON file.")
                   if mqttEnabled:
                       ble2mqtt.heartbeat()
                       ble2mqtt.send_bt(data)
                       print("Published to MQTT.....")
                       ble2mqtt.b_led_blink()
                       ble2json.remove_contents_from_bledata_file(ble2json.bledata_file_path)
                       if not ble2json.is_character_in_bledata_file(ble2json.bledata_file_path, character_to_check):
                              ble2json.append_character_to_bledata_file(ble2json.bledata_file_path, character_to_check)
                              print(f"Appended '{character_to_check}' to the JSON file.")
                       else:
                              print(f"'{character_to_check}' is already in the JSON file.")
                       #subprocess.run(['sudo', 'service', 'bluetooth', 'start'], check=True)
                       stop_flag = True
                       scanner._mon.toggle_scan(True)
                   if httpEnabled:
                       ble2http.heartbeat()
                       ble2http.send_bt(data)
                       ble2mqtt.b_led_blink()
       else:
            print("No internet connectivity. Retrying Connection...")
            ble2mqtt.g_led_blink()
            retry_connection()
            ble2json.remove_contents_from_bledata_file(ble2json.bledata_file_path)
            if not ble2json.is_character_in_bledata_file(ble2json.bledata_file_path, character_to_check):
                   ble2json.append_character_to_bledata_file(ble2json.bledata_file_path, character_to_check)
                   print(f"Appended '{character_to_check}' to the JSON file.")
            else:
                   print(f"'{character_to_check}' is already in the JSON file.")

    except Exception as e:
        run_flag = False
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    try:
        timeout_seconds = 30  # Adjust the timeout value as needed
        watchdog_thread = threading.Thread(target=watchdog_timer, args=(timeout_seconds,))
        watchdog_thread.start()
        main_loop()
    except KeyboardInterrupt:
           scanner.stop()
           ble2mqtt.r_led_off()
           ble2mqtt.g_led_off()
           ble2mqtt.b_led_off()
           if mqttEnabled:
               ble2mqtt.end()
           if httpEnabled:
               ble2http.end()
           print("\nExiting application\n")
           sys.exit(0)

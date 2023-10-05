import time
import sys
import json
import blegateway
import config
import subprocess
import ble2json
#import bleconfig
import RPi.GPIO as gpio

gpio.setmode(gpio.BOARD)

r_led = 40

gpio.setup(r_led,gpio.OUT)

gpio.output(r_led,0)
time.sleep(0.2)
gpio.output(r_led,1)

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
influxEnabled = config.get_config('endpoints')['influxEnabled']

blescantime = config.get_config('optime')['scantime']
blepushtime = config.get_config('optime')['pushtime']

if mqttEnabled:
    import ble2mqtt
if httpEnabled:
    import ble2http
if influxEnabled:
    import ble2influx

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

def callback(bt_addr, rssi, packet, dec, smoothedRSSI):
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
               print("Storing BLE data in file...")
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


def main_loop():
    RSSIen = config.get_config('filters')['rssiThreshold']
    if (RSSIen):
        RSSI = config.get_config('filters')['rssi']
    else:
        RSSI = -999
    if mqttEnabled:
        ble2mqtt.MQTT()
    if httpEnabled:
        ble2mqtt.HTTP()
    if influxEnabled:
        ble2mqtt.INFLUX()
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
    ble2mqtt.receive_config()
    while True:
        #ble2mqtt.receive_config()
        if config.get_config('bleDevice')['bleDevice'] == 1:
            time.sleep(blepushtime)
            if mqttEnabled:
                ble2mqtt.heartbeat()
            if httpEnabled:
                ble2http.heartbeat()
            if influxEnabled:
                ble2influx.heartbeat()
        else:
            print("BlePushTime:", blepushtime)
            time.sleep(blepushtime)
            scanner._mon.toggle_scan(False)
            print("Sending gateway data...")
            ble2mqtt.heartbeat()
            print("Sending BLE data...")
            # Read the last character of the JSON file
            last_character = ble2json.read_last_character_in_bledata_file(ble2json.bledata_file_path)
            if last_character is not None and last_character != ']':
               ble2json.replace_last_character_in_bledata_file(ble2json.bledata_file_path)
               print(f"Replaced last character with '{ble2json.replacement_character}' in the JSON file.")
            else:
                 print("The last character is either None or already ']'.")
            with open(ble2json.bledata_file_path, "r") as json_file:
                 data = json.load(json_file)
                 if mqttEnabled:
                    ble2mqtt.send_bt(data)
                    print("Published to MQTT.....")
                 if httpEnabled:
                    ble2http.send_bt(data)
                    print("Published to HTTP.....")
                 if influxEnabled:
                    ble2influx.send_bt(data)
                    print("Published to INFLUX.....")
            ble2json.remove_contents_from_bledata_file(ble2json.bledata_file_path)
            scanner._mon.toggle_scan(True)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        scanner.stop()
        if mqttEnabled:
            ble2mqtt.end()
        print("\nExiting application\n")
        sys.exit(0)

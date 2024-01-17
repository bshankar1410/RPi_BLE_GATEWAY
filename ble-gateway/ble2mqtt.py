import paho.mqtt.client as mqtt
import ssl
import time
import json
import config
import blegateway
import ble2json
import RPi.GPIO as gpio
import subprocess
import sys

sys.path.append('/home/pi/test123/testgitdownload.py')

from testgitdownload.py import clone_repository

gpio.setmode(gpio.BOARD)

r_led = 40
g_led = 38
b_led = 36

gpio.setup(r_led,gpio.OUT)
gpio.setup(g_led,gpio.OUT)
gpio.setup(b_led,gpio.OUT)

gpio.output(b_led,0)

mqttCONFIG = config.get_config('mqtt')

ids = config.get_config('identifiers')

BTOPIC = ids['location'] + "/" + ids['zone']
print("Main Topic: " + BTOPIC)
GWTOPIC = 'Gateway/' + ids['location'] + "/" + ids['zone']
print("Gateway Topic: " + GWTOPIC)
RCTOPIC = "RPiGW"
print("Config Topic: " + RCTOPIC)
OTATOPIC = "OTARPiGW"
print("OTA Topic: " + OTATOPIC)


DISCONNECTED = 0
CONNECTING = 1
CONNECTED = 2

if mqttCONFIG['ssl']:
    ROOT_CA = mqttCONFIG['ca']
    CLIENT_CERT = mqttCONFIG['cert']
    PRIVATE_KEY = mqttCONFIG['key']

def r_led_on():
    gpio.output(r_led,1)

def g_led_on():
    gpio.output(g_led,1)

def b_led_on():
    gpio.output(b_led,1)

def r_led_off():
    gpio.output(r_led,0)

def g_led_off():
    gpio.output(g_led,0)

def b_led_off():
    gpio.output(b_led,0)

def b_led_blink():
    gpio.output(b_led,0)
    time.sleep(0.3)
    gpio.output(b_led,1)
    time.sleep(0.3)

def g_led_blink():
    gpio.output(g_led,0)
    time.sleep(0.3)
    gpio.output(g_led,1)
    time.sleep(0.3)

def MQTT():
    isSSL = mqttCONFIG['ssl']
    if isSSL:
        ROOT_CA = mqttCONFIG['ca']
        CLIENT_CERT = mqttCONFIG['cert']
        PRIVATE_KEY = mqttCONFIG['key']
    state = DISCONNECTED
    global client
    client = mqtt.Client()
    if mqttCONFIG['user'] != None and \
        mqttCONFIG['password'] != None :
        client.username_pw_set(mqttCONFIG['user'], password=mqttCONFIG['password'])
    if isSSL == True:
        client.tls_set(ca_certs=ROOT_CA, certfile=CLIENT_CERT, keyfile=PRIVATE_KEY, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)

    while state != CONNECTED:
        try:
            state = CONNECTING
            client.connect(mqttCONFIG['host'], mqttCONFIG['port'], 60)
            state = CONNECTED
        except:
            print('Could not establish MQTT connection')
            b_led_blink()
    if state == CONNECTED:
            b_led_on()
            print('MQTT Client Connected')
    client.loop_start()


def heartbeat():
    client.publish( GWTOPIC, json.dumps(blegateway.fill_heartbeat()), qos=1, retain=False )

#def send_bt(bt_addr, message):
def send_bt(message):
    #print("BT Address:",bt_addr)
    #client.publish( TOPIC + "/" + bt_addr, json.dumps(message), qos=1, retain=False )
    client.publish( BTOPIC, json.dumps(message), qos=1, retain=False)

def send_ota_status():
    msg = {"otaupdate": {
             "ota_status": True
           }
          }
    client.publish(OTATOPIC, json.dumps(msg), qos=1, retain=False)

def GW_Reboot():
    print("System reboot....")
    time.sleep(0.3)
    b_led_off()
    g_led_off()
    r_led_off()
    time.sleep(0.3)
    try:
        print("System Reboot")
        time.sleep(3)
        subprocess.run(["sudo", "reboot"])
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def update_wifi_config(ssid, password):
    try:
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'r') as file:
            lines = file.readlines()
            time.sleep(0.1)
        # Find the indices of the second network configuration
        network_indices = [i for i, line in enumerate(lines) if 'network={' in line]
        if len(network_indices) >= 2:
            start_index = network_indices[1]
            # Update the SSID and PSK for the second network
            lines[start_index + 1] = f'    ssid="{ssid}"\n'
            lines[start_index + 2] = f'    psk="{password}"\n'
            # Rewrite the contents back to the file
            with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as file:
                 file.writelines(lines)
                 print("Network configuration updated successfully.")
        else:
           print("The file does not contain two network configurations.")
    except Exception as e:
        print(f"Error updating wpa_supplicant.conf file: {str(e)}")

def check_network_manager_status():
    try:
        # Check the status of NetworkManager
        status_command = "sudo service NetworkManager status"
        status_output = subprocess.check_output(status_command, shell=True, text=True)
        return "Active: active (running)" in status_output
    except subprocess.CalledProcessError:
        return False

def enable_network_manager():
    try:
        # Start the NetworkManager service
        start_command = "sudo service NetworkManager start"
        subprocess.run(start_command, shell=True, check=True)
        print("NetworkManager started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting NetworkManager: {e}")

def add_wifi_connection(ssid, password):
    if not check_network_manager_status():
        print("NetworkManager is not running. Starting NetworkManager...")
        enable_network_manager()
    try:
        # Form the nmcli command to add a Wi-Fi connection
        command = f"sudo nmcli device wifi connect '{ssid}' password '{password}'"
        # Run the nmcli command
        subprocess.run(command, shell=True, check=True)
        print(f"Successfully added Wi-Fi connection for {ssid}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


def on_publish(client, userdata, mid):
    print(f"Message Published with MID: {mid}")


# MQTT message callback
def on_message(client, userdata, message):
    try:
        received_data = message.payload.decode("utf-8")
        json_data = json.loads(received_data)
        print(json_data)
        new_bleDevice = json_data.get("bleDevice", {}) # Extract the "bleDevice" section
        new_wificonf = json_data.get("wificonf", {}) # Extract the "wificonf"  section
        new_filters = json_data.get("filters",{}) # Extract the "filters" section
        new_optime = json_data.get("optime",{}) # Extract the "optime" section
        new_names = json_data.get("names",{}) # Extract the "names" section
        new_identifiers = json_data.get("identifiers",{}) # Extract the "identifiers" section
        new_endpoints = json_data.get("endpoints",{}) # Extract the "endpoints" section
        new_mqtt = json_data.get("mqtt",{}) # Extract the "mqtt" section
        new_http = json_data.get("http",{}) # Extract the "http" section
        new_ota_update = json_data.get("ota_update",{}) # Extract the "influx" section
        with open(ble2json.config_file_path, "r", encoding = "utf-8") as json_file:
             existing_data = json.load(json_file)
             if new_wificonf:
                 print("Configuring WiFi...")
                 existing_data["wificonf"] = new_wificonf
                 updated_data = existing_data
                 ble2json.save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
                 with open(ble2json.config_file_path, 'r') as json_file:
                      data = json.load(json_file)
                      wificonf = data.get("wificonf")
                      ssid = wificonf.get("ssid")
                      password = wificonf.get("psk")
                      update_wifi_config(ssid, password)
                      add_wifi_connection(ssid, password)
                      GW_Reboot()
             elif new_bleDevice:
                 print("Configuring bleDevice...")
                 existing_data["bleDevice"] = new_bleDevice
                 updated_data = existing_data
                 ble2json.save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             elif new_filters:
                 print("Configuring filters...")
                 existing_data["filters"] = new_filters
                 updated_data = existing_data
                 ble2json.save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
                 GW_Reboot()
             elif new_optime:
                 print("Configuring optime...")
                 existing_data["optime"] = new_optime
                 updated_data = existing_data
                 ble2json.save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
                 GW_Reboot()
             elif new_names:
                 print("Configuring names...")
                 existing_data["names"] = new_names
                 updated_data = existing_data
                 ble2json.save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             elif new_identifiers:
                 print("Configuring identifiers...")
                 existing_data["identifiers"] = new_identifiers
                 updated_data = existing_data
                 ble2json.save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             elif new_endpoints:
                 print("Configuring endpoints...")
                 existing_data["endpoints"] = new_endpoints
                 updated_data = existing_data
                 ble2json.save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             elif new_mqtt:
                 print("Configuring mqtt...")
                 existing_data["mqtt"] = new_mqtt
                 updated_data = existing_data
                 ble2json.save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
                 GW_Reboot()
             elif new_http:
                 print("Configuring http...")
                 existing_data["http"] = new_http
                 updated_data = existing_data
                 ble2json.save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
                 GW_Reboot()
             elif new_ota_update:
                 print("Configuring ota json data...")
                 existing_data["ota_update"] = new_ota_update
                 updated_data = existing_data
                 ble2json.save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
                 otaCONFIG = config.get_config('ota_update')
                 if otaCONFIG['ota_status'] == True:
                    #bleota.download_and_verify_github_repo()
                    clone_repository()
                    send_ota_status()
                    time.sleep(1)
                    GW_Reboot()
             else:
                 print("No Update Needed...")
       # ble2json.save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
    except json.JSONDecodeError as e:
        print(f"Error decoding MQTT message: {str(e)}")


def receive_config():
    # Subscribe to the MQTT topic
    client.subscribe(RCTOPIC)
    # Attach the on_publish callback
    client.on_publish = on_publish
    # Set the MQTT message callback
    client.on_message = on_message


def end():
    client.loop_stop()
    client.disconnect()

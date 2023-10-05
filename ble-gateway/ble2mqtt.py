import paho.mqtt.client as mqtt
import ssl
import time
import json
import config
import blegateway
import ble2json
import RPi.GPIO as gpio

gpio.setmode(gpio.BOARD)

b_led = 36

gpio.setup(b_led,gpio.OUT)

gpio.output(b_led,0)

mqttCONFIG = config.get_config('mqtt')
ids = config.get_config('identifiers')

BTOPIC = ids['location'] + "/" + ids['zone']
print("Main Topic: " + BTOPIC)
GWTOPIC = 'Gateway/' + ids['location'] + "/" + ids['zone']
print("Gateway Topic: " + GWTOPIC)
#RCTOPIC = 'Config/blegateway'
RCTOPIC = "RPiGW"
print("Config Topic: " + RCTOPIC)

DISCONNECTED = 0
CONNECTING = 1
CONNECTED = 2

if mqttCONFIG['ssl']:
    ROOT_CA = mqttCONFIG['ca']
    CLIENT_CERT = mqttCONFIG['cert']
    PRIVATE_KEY = mqttCONFIG['key']

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
            gpio.output(b_led,1)
            print('Could not establish MQTT connection')
            time.sleep(0.3)
            gpio.output(b_led,0)
            time.sleep(0.3)
    if state == CONNECTED:
            gpio.output(b_led,1)
            print('MQTT Client Connected')
    client.loop_start()



def heartbeat():
    client.publish( GWTOPIC, json.dumps(blegateway.fill_heartbeat()), qos=1, retain=False )

#def send_bt(bt_addr, message):
def send_bt(message):
    #print("BT Address:",bt_addr)
    #client.publish( TOPIC + "/" + bt_addr, json.dumps(message), qos=1, retain=False )
    client.publish( BTOPIC, json.dumps(message), qos=1, retain=False )

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
        new_influx = json_data.get("influx",{}) # Extract the "influx" section
        with open(ble2json.config_file_path, "r", encoding = "utf-8") as json_file:
             existing_data = json.load(json_file)
             if new_wificonf:
                 print("Configuring WiFi...")
                 existing_data["wificonf"] = new_wificonf
                 updated_data = existing_data
                 #save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             elif new_bleDevice:
                 print("Configuring bleDevice...")
                 existing_data["bleDevice"] = new_bleDevice
                 updated_data = existing_data
                 #save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             elif new_filters:
                 print("Configuring filters...")
                 existing_data["filters"] = new_filters
                 updated_data = existing_data
                 #save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             elif new_optime:
                 print("Configuring optime...")
                 existing_data["optime"] = new_optime
                 updated_data = existing_data
                 #save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             elif new_names:
                 print("Configuring names...")
                 existing_data["names"] = new_names
                 updated_data = existing_data
                 #save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             elif new_identifiers:
                 print("Configuring identifiers...")
                 existing_data["identifiers"] = new_identifiers
                 updated_data = existing_data
                 #save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             elif new_endpoints:
                 print("Configuring endpoints...")
                 existing_data["endpoints"] = new_endpoints
                 updated_data = existing_data
                 #save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             elif new_mqtt:
                 print("Configuring mqtt...")
                 existing_data["mqtt"] = new_mqtt
                 updated_data = existing_data
                 #save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             elif new_http:
                 print("Configuring http...")
                 existing_data["http"] = new_http
                 updated_data = existing_data
                 #save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             elif new_influx:
                 print("Configuring influx...")
                 existing_data["influx"] = new_influx
                 updated_data = existing_data
                 #save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
             else:
                 print("No Update Needed...")
        ble2json.save_config_to_configblegateway_file(ble2json.config_file_path,updated_data)
    except json.JSONDecodeError as e:
        print(f"Error decoding MQTT message: {str(e)}")


def receive_config():
    # Subscribe to the MQTT topic
    client.subscribe(RCTOPIC)
    # Set the MQTT message callback
    client.on_message = on_message


def end():
    client.loop_stop()
    client.disconnect()

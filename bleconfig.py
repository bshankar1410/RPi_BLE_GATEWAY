import json
import paho.mqtt.client as mqtt
import config

mqttEnabled = config.get_config('endpoints')['mqttEnabled']
httpEnabled = config.get_config('endpoints')['httpEnabled']
influxEnabled = config.get_config('endpoints')['influxEnabled']

if mqttEnabled:
    import ble2mqtt
if httpEnabled:
    import ble2http
if influxEnabled:
    import ble2influx


# Function to save updated JSON data to a file
def save_json_to_file(file_path, json_data):
    try:
        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
        print(f"Updated JSON file: {file_path}")
    except Exception as e:
        print(f"Error saving JSON data to file: {str(e)}")

# MQTT parameters
mqtt_broker = "45.79.117.227"
mqtt_port = 1883
mqtt_topic = "RPiGW"
mqtt_username = "fervid"
mqtt_password = "pU8zBqQj"

# JSON file path
file_path = "example.json"  # Replace with your JSON file path

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
        if new_wificonf:
           with open(file_path, "r", encoding = "utf-8") as json_file:
                 print("Configuring WiFi...")
                 existing_data = json.load(json_file)
                 existing_data["wificonf"] = new_wificonf
                 updated_data = existing_data
                 save_json_to_file(file_path,updated_data)
        elif new_bleDevice:
           with open(file_path, "r", encoding = "utf-8") as json_file:
                 print("Configuring bleDevice...")
                 existing_data = json.load(json_file)
                 existing_data["bleDevice"] = new_bleDevice
                 updated_data = existing_data
                 save_json_to_file(file_path, updated_data)
        elif new_filters:
           with open(file_path, "r", encoding = "utf-8") as json_file:
                 print("Configuring filters...")
                 existing_data = json.load(json_file)
                 existing_data["filters"] = new_filters
                 updated_data = existing_data
                 save_json_to_file(file_path, updated_data)
        elif new_optime:
           with open(file_path, "r", encoding = "utf-8") as json_file:
                 print("Configuring optime...")
                 existing_data = json.load(json_file)
                 existing_data["optime"] = new_optime
                 updated_data = existing_data
                 save_json_to_file(file_path, updated_data)
        elif new_names:
           with open(file_path, "r", encoding = "utf-8") as json_file:
                 print("Configuring names...")
                 existing_data = json.load(json_file)
                 existing_data["names"] = new_names
                 updated_data = existing_data
                 save_json_to_file(file_path, updated_data)
        elif new_identifiers:
           with open(file_path, "r", encoding = "utf-8") as json_file:
                 print("Configuring identifiers...")
                 existing_data = json.load(json_file)
                 existing_data["identifiers"] = new_identifiers
                 updated_data = existing_data
                 save_json_to_file(file_path, updated_data)
        elif new_endpoints:
           with open(file_path, "r", encoding = "utf-8") as json_file:
                 print("Configuring endpoints...")
                 existing_data = json.load(json_file)
                 existing_data["endpoints"] = new_endpoints
                 updated_data = existing_data
                 save_json_to_file(file_path, updated_data)
        elif new_mqtt:
           with open(file_path, "r", encoding = "utf-8") as json_file:
                 print("Configuring mqtt...")
                 existing_data = json.load(json_file)
                 existing_data["mqtt"] = new_mqtt
                 updated_data = existing_data
                 save_json_to_file(file_path, updated_data)
        elif new_http:
           with open(file_path, "r", encoding = "utf-8") as json_file:
                 print("Configuring http...")
                 existing_data = json.load(json_file)
                 existing_data["http"] = new_http
                 updated_data = existing_data
                 save_json_to_file(file_path, updated_data)
        elif new_influx:
           with open(file_path, "r", encoding = "utf-8") as json_file:
                 print("Configuring influx...")
                 existing_data = json.load(json_file)
                 existing_data["influx"] = new_influx
                 updated_data = existing_data
                 save_json_to_file(file_path, updated_data)
        else:
            print("No Update Needed...")
    except json.JSONDecodeError as e:
        print(f"Error decoding MQTT message: {str(e)}")

# Create an MQTT client and connect to the broker
client = mqtt.Client()
client.username_pw_set(username=mqtt_username, password=mqtt_password)
client.connect(mqtt_broker, mqtt_port)

# Subscribe to the MQTT topic
client.subscribe(mqtt_topic)

# Set the MQTT message callback
client.on_message = on_message

# Start the MQTT client loop
client.loop_forever()

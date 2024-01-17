import json

try:
  # Allows for test config file to be used during development
  config = json.load(open('configblegateway.json',))
except:
  config = json.load(open('blegateway.json',))

def get_config(section):
  if section == 'bleDevice' or section == 'filters' or \
    section == 'identifiers' or section == 'endpoints' or \
      section == 'optime' or section == 'names':
      return config[section]
  elif section == 'mqtt' or section == 'http' or \
    section == 'ota_update':
    if section in config:
      return config[section]
  else:
    print('Invalid Section given')
    return None

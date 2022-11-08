import json


def get_data_from_config(filename):
    file = open(filename)
    return json.load(file)

def get_port_from_config(filename):
    data = get_data_from_config(filename)
    return data["port"]



#print(get_port_from_config("config.json"))
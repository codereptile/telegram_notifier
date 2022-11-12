import json


def get_data_from_config(filename):
    file = open(filename)
    return json.load(file)


def get_port_from_config(data):
    return data["port"]


def get_host_from_config(data):
    return data["host"]


def get_instruments(data):
    return data["instruments"]


def get_instrument(data, instrument_name):
    instruments = get_instruments(data)
    return instruments[instrument_name]


def get_instrument_enable(data, instrument_name):
    instrument = get_instrument(data, instrument_name)
    return instrument["enable"]


def get_instrument_frequency(data, instrument_name):
    instrument = get_instrument(data, instrument_name)
    return instrument["frequency"]

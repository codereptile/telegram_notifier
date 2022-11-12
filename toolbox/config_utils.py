import json


def load_config(filename):
    file = open(filename)
    return json.load(file)


def get_instruments(data):
    return data["instruments"]


def get_instrument(data, instrument_name):
    instruments = get_instruments(data)
    return instruments[instrument_name]


def get_instrument_enable(data, instrument_name):
    instrument = get_instrument(data, instrument_name)
    return instrument["enable"]

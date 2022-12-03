import sys


def get_server_priority(server_config):
    try:
        return server_config["notification_priority"]
    except:
        sys.exit("No server priority in config")


def get_message_protocol(server_config):
    try:
        return server_config["message_protocol"]
    except:
        sys.exit("No message protocol in config")


def get_host(server_config):
    try:
        return server_config["host"]
    except:
        sys.exit("No server host in config")


def get_port(server_config):
    try:
        return server_config["port"]
    except:
        sys.exit("No server port in config")

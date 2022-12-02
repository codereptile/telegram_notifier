def get_server_priority(server_config):
    try:
        return server_config["notification_priority"]
    except:
        print("Server haven't priority")
        return 1


def get_message_protocol(server_config):
    try:
        return server_config["message_protocol"]
    except:
        print("Server haven't message protocol")
        return ""


def get_host(server_config):
    try:
        return server_config["host"]
    except:
        print("Server config haven't host. Set default host 127.0.0.1")
        return "127.0.0.1"


def get_port(server_config):
    try:
        return server_config["port"]
    except:
        print("Server config haven't port. Set default port 8080")
        return 8080

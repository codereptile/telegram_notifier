import json
import sys
import datetime


class Client:
    def __init__(self, name, config):
        self.name = name
        self.last_update_time = None
        self.config = config

        self.last_known_disk_usage = -1
        self.next_disk_usage_trigger = self.config["disk_usage_minimal_trigger"]

    def update_disk_usage(self, message_handler, message_json):
        self.last_known_disk_usage = int(message_json["value"])
        if self.last_known_disk_usage > self.next_disk_usage_trigger:
            self.next_disk_usage_trigger = self.last_known_disk_usage + self.config["disk_usage_trigger_step"]
            message_handler.add_message(
                "WARNING from << " + self.name + " >>:\nDisk usage: " + str(self.last_known_disk_usage) + "%")

    def is_online(self):
        time_since_last_update = datetime.datetime.now() - self.last_update_time
        if time_since_last_update.total_seconds() < self.config["client_online_timeout"]:
            return True
        else:
            return False

    def status(self):
        message_string = "Status for << " + self.name + " >>:\n" + \
                         "Last update: " + str(self.last_update_time) + "\n" + \
                         "Is online: " + str(self.is_online()) + "\n" + \
                         "Last know disk usage: " + str(self.last_known_disk_usage) + "%"
        return message_string


class ClientHandler:
    def __init__(self, config):
        self.clients = {}
        self.config = config

    def add_client(self, name):
        if self.clients.get(name) is None:
            self.clients[name] = Client(name, self.config)
        else:
            print("DUPLICATE CLIENT:" + name, file=sys.stderr)

    def process_message(self, message_handler, message):
        message_json = json.loads(message)

        if self.clients.get(message_json["client_name"]) is None:
            self.add_client(message_json["client_name"])

        client = self.clients[message_json["client_name"]]
        client.last_update_time = datetime.datetime.now()

        if message_json["message_type"] == "instant_message":
            message_handler.add_message(
                "Got instant message from << " + message_json["client_name"] + " >>:\n" + message_json["value"])
        elif message_json["message_type"] == "supervisor_event_listener":
            message_handler.add_message(
                "Got supervisor update from << " + message_json["client_name"] + " >>:\n" + message_json[
                    "value"])
        elif message_json["message_type"] == "check_disk_usage":
            client.update_disk_usage(message_handler, message_json)
        else:
            print("UNKNOWN MESSAGE TYPE:" + message, file=sys.stderr)

    def status(self):
        message_string = ""
        for client_name in self.clients:
            message_string += self.clients[client_name].status() + "\n"
        if message_string == "":
            message_string = "No clients "
        return message_string

    def check_clients

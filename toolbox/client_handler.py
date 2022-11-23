import json
import sys
import datetime


class Client:

    def __init__(self, client_config):
        self.name = client_config["name"]
        self.last_update_time = None
        self.config = client_config

        self.last_known_disk_usage = -1
        self.next_disk_usage_trigger = self.config["tasks"]["check_disk_usage"]["handler_type"][
            "minimal_trigger"]
        self.last_known_cpu_usage = -1
        self.next_cpu_usage_trigger = self.config["tasks"]["check_cpu_usage"]["handler_type"][
            "minimal_trigger"]
        self.last_known_ram_usage = -1
        self.next_ram_usage_trigger = self.config["tasks"]["check_ram_usage"]["handler_type"][
            "minimal_trigger"]

    def check_trigger(self, last_task_info, next_task_trigger, task_step, task_name, message_handler):
        if last_task_info > next_task_trigger:
            next_task_trigger = last_task_info + task_step
            message_handler.add_message("WARNING from << " + self.name + " >>:\n" + task_name + ": " +
                                        str(last_task_info) + "%")
            return next_task_trigger
        else:
            return next_task_trigger

    def update_parameter(self, message_handler, message_json):

        if message_json["message_type"] == "check_disk_usage":
            self.last_known_disk_usage = int(message_json["value"])
            step = self.config["tasks"]["check_disk_usage"]["handler_type"]["trigger_step"]

            self.next_disk_usage_trigger = self.check_trigger(self.last_known_disk_usage, self.next_disk_usage_trigger,
                                                              step,
                                                              "Disk usage", message_handler)

            if self.last_known_disk_usage < self.config["tasks"]["check_disk_usage"]["handler_type"]["minimal_trigger"]:
                self.next_disk_usage_trigger = self.config["tasks"]["check_disk_usage"]["handler_type"][
                    "minimal_trigger"]
        elif message_json["message_type"] == "check_cpu_usage":
            self.last_known_cpu_usage = int(message_json["value"])
            try:
                step = self.config["tasks"]["check_cpu_usage"]["handler_type"]["trigger_step"]
            except:
                step = 1000

            self.next_cpu_usage_trigger = self.check_trigger(self.last_known_cpu_usage, self.next_cpu_usage_trigger,
                                                             step,
                                                             "CPU usage", message_handler)

            if self.last_known_disk_usage < self.config["tasks"]["check_cpu_usage"]["handler_type"]["minimal_trigger"]:
                self.next_disk_usage_trigger = self.config["tasks"]["check_cpu_usage"]["handler_type"][
                    "minimal_trigger"]
        elif message_json["message_type"] == "check_ram_usage":
            self.last_known_ram_usage = int(message_json["value"])
            step = self.config["tasks"]["check_ram_usage"]["handler_type"]["trigger_step"]

            self.next_ram_usage_trigger = self.check_trigger(self.last_known_ram_usage, self.next_ram_usage_trigger,
                                                             step,
                                                             "RAM usage", message_handler)

            if self.last_known_disk_usage < self.config["tasks"]["check_ram_usage"]["handler_type"]["minimal_trigger"]:
                self.next_disk_usage_trigger = self.config["tasks"]["check_ram_usage"]["handler_type"][
                    "minimal_trigger"]

    def is_online(self):
        if self.last_update_time is None:
            return False
        time_since_last_update = datetime.datetime.now() - self.last_update_time
        if time_since_last_update.total_seconds() < self.config["client_online_timeout"]:
            return True
        else:
            return False

    def status(self):
        message_string = "Status for << " + self.name + " >>:\n" + \
                         "Last update: " + str(self.last_update_time) + "\n" + \
                         "Is online: " + str(self.is_online()) + "\n" + \
                         "Last know disk usage: " + str(self.last_known_disk_usage) + "%\n" + \
                         "Last know CPU usage: " + str(self.last_known_cpu_usage) + "%\n" + \
                         "Last know RAM usage: " + str(self.last_known_ram_usage) + "%\n"
        return message_string


class ClientHandler:
    def __init__(self, config):
        self.clients = {}
        self.offline_clients = {}
        self.config = config

    def add_client(self, client_config):
        if self.clients.get(client_config["name"]) is None:
            self.clients[client_config["name"]] = Client(client_config)
        else:
            print("DUPLICATE CLIENT:" + client_config["name"], file=sys.stderr)

    def load_clients(self):
        from os import walk

        config_files = []
        for (dirpath, dirnames, filenames) in walk("conf.d"):
            config_files.extend(filenames)

        for config_file in config_files:
            try:
                client_config = json.load(open("conf.d/" + config_file))
                self.add_client(client_config)
                self.offline_clients[client_config["name"]] = self.clients[client_config["name"]]
            except Exception as e:
                print("COULD NOT LOAD CLIENT CONFIG: " + config_file, file=sys.stderr)
                print(e, file=sys.stderr)

    def process_message(self, message_handler, message):
        message_json = json.loads(message)

        if self.clients.get(message_json["client_name"]) is None:
            print("UNKNOWN CLIENT: " + message_json["client_name"], file=sys.stderr)
            return

        client = self.clients[message_json["client_name"]]
        client.last_update_time = datetime.datetime.now()
        self.offline_clients.pop(message_json["client_name"], None)

        if message_json["message_type"] == "get_config":
            return json.dumps(client.config)
        elif message_json["message_type"] == "instant_message":
            message_handler.add_message(
                "Got instant message from << " + message_json["client_name"] + " >>:\n" + message_json["value"])
        elif message_json["message_type"] == "supervisor_event_listener":
            message_handler.add_message(
                "Got supervisor update from << " + message_json["client_name"] + " >>:\n" + message_json[
                    "value"])
        elif message_json["message_class"] == "update_parameter_by_trigger":
            if self.config["notification_priority"] \
                    <= client.config["tasks"][message_json["message_type"]]["handler_type"]["message_priority"]:
                client.update_parameter(message_handler, message_json)
        else:
            print("UNKNOWN MESSAGE TYPE:" + message, file=sys.stderr)
            return "UNKNOWN MESSAGE TYPE"
        return "Accepted"

    def status(self):
        message_string = ""
        for client_name in self.clients:
            message_string += self.clients[client_name].status() + "\n"
        if message_string == "":
            message_string = "No clients "
        return message_string

    def check_clients(self, **kwargs):

        for client_name in self.clients:
            client = self.clients[client_name]
            if not client.is_online() and self.offline_clients.get(client_name) is None:
                self.offline_clients[client_name] = client
                kwargs["message_handler"].add_message("CRITICAL: Client << " + client_name + " >> stopped responding")

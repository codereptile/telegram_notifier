import sys


# Handle errors of client config from server
def get_client_name(client_config):
    try:
        return client_config["name"]
    except:
        sys.exit("Client's config haven't client's name")


def get_client_tasks(client_config):
    try:
        return client_config["tasks"]
    except:
        sys.exit(get_client_name(client_config) + "'s config haven't tasks field")


def get_task_trigger(client_config, task_name):
    try:
        return client_config["tasks"][task_name]["handler"]["minimal_trigger"]
    except:
        sys.exit(get_client_name(client_config) + "'s task " + task_name + " haven't trigger field")


def get_task_trigger_step(client_config, task_name):
    try:
        return client_config["tasks"][task_name]["handler"]["trigger_step"]
    except:
        sys.exit(get_client_name(client_config) + "'s task " + task_name + " haven't trigger step field")


def get_task_priority(client_config, task_name):
    try:
        return client_config["tasks"][task_name]["handler"]["message_priority"]
    except:
        sys.exit(get_client_name(client_config) + "'s task " + task_name + " haven't priority field")


def get_client_timeout(client_config):
    try:
        return client_config["client_online_timeout"]
    except:
        sys.exit("Client " + get_client_name(client_config) + " haven't timeout")


def get_task_name(client_config, task_name):
    try:
        return client_config["tasks"][task_name]["task_name"]
    except:
        sys.exit("Task of client " + get_client_name(client_config) + " haven't task name")


def get_task_enability(client_config, task_name):
    try:
        return client_config["tasks"][task_name]["enable"]
    except:
        sys.exit("task of client " + get_client_name(client_config) + " haven't enability")


def get_supervisor_enability(client_config):
    try:
        return client_config["supervisor_event_listener"]
    except:
        sys.exit("Client " + get_client_name(client_config) + " haven't supervisor status")

# Handle errors of client's initial config


def get_client_initial_name(initial_config):
    try:
        return initial_config["client_name"]
    except:
        sys.exit("Client's initial config haven't client's name")


def get_client_initial_host(initial_config):
    try:
        return initial_config["host"]
    except:
        sys.exit("Client's initial config haven't client's host")


def get_client_initial_port(initial_config):
    try:
        return initial_config["port"]
    except:
        sys.exit("Client's initial config haven't client's port")

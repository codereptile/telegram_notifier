def get_client_name(client_config):
    try:
        return client_config["name"]
    except:
        print("Client have no name")
        return ""


def get_client_tasks(client_config):
    try:
        return client_config["tasks"]
    except:
        print("Client " + get_client_name(client_config) + " have no tasks")
        return []


def get_task_trigger(client_config, task_name):
    try:
        return client_config["tasks"][task_name]["handler"]["minimal_trigger"]
    except:
        print("Cannot get minimal trigger for client " + get_client_name(client_config))
        return 1000  # Don't know...


def get_task_trigger_step(client_config, task_name):
    try:
        return client_config["tasks"][task_name]["handler"]["trigger_step"]
    except:
        print("Cannot get trigger step for client " + get_client_name(client_config))
        return 1000


def get_task_priority(client_config, task_name):
    try:
        return client_config["tasks"][task_name]["handler"]["message_priority"]
    except:
        print("Cannot get task priority for client " + get_client_name(client_config))
        return 5


def get_client_timeout(client_config):
    try:
        return client_config["client_online_timeout"]
    except:
        print("Client " + get_client_name(client_config) + " haven't timeout")
        return 1000


def get_task_name(client_config, task_name):
    try:
        return client_config["tasks"][task_name]["task_name"]
    except:
        print("Task of client " + get_client_name(client_config) + " haven't task name")
        return ""


def get_task_enability(client_config, task_name):
    try:
        return client_config["tasks"][task_name]["enable"]
    except:
        print("task of client " + get_client_name(client_config) + " haven't enability")
        return 0


def get_supervisor_enability(client_config):
    try:
        return client_config["supervisor_event_listener"]
    except:
        print("Client " + get_client_name(client_config) + " haven't supervisor status")
        return 0

import re
import subprocess


def check_disk_usage(message_handler, config_arguments, config_handler_type):
    filesystem = config_arguments["filesystem"]
    output_string = subprocess.run(["df", "-h"], capture_output=True).stdout.decode("utf-8")
    match = re.search(filesystem, output_string)
    if match is None:
        return "SERVER STATUS CHECK FAILED! (df -h)"
    match = re.search("[0-9]*%", match[0])
    if match is None:
        return "SERVER STATUS CHECK FAILED! (df -h)"
    disk_usage_percentage = int(match[0][:-1])

    message_json = {'message_class': config_handler_type["message_class"], 'message_type': 'check_disk_usage',
                    'value': str(disk_usage_percentage)}

    message_handler.add_message(message_json)


def check_cpu_usage(message_handler, config_arguments, config_handler_type):
    load_average_string = subprocess.run(["cat", "/proc/loadavg"], capture_output=True).stdout.decode("utf-8")
    number_of_cores_string = subprocess.run(["grep", "-c", "^processor", "/proc/cpuinfo"],
                                            capture_output=True).stdout.decode("utf-8")
    load_average = float(load_average_string.split(" ")[0])
    number_of_cores = int(number_of_cores_string)

    cpu_usage_percentage = int(load_average / number_of_cores * 100)

    message_json = {'message_class': config_handler_type["message_class"], 'message_type': 'check_cpu_usage',
                    'value': cpu_usage_percentage}

    message_handler.add_message(message_json)


def check_ram_usage(message_handler, config_arguments, config_handler_type):
    output_string = subprocess.run(["cat", "/proc/meminfo"], capture_output=True).stdout.decode("utf-8")
    total_ram = int(output_string.split("\n")[0].split(" ")[-2])
    available_ram = int(output_string.split("\n")[2].split(" ")[-2])
    ram_usage_percentage = int((total_ram - available_ram) / total_ram * 100)

    message_json = {'message_class': config_handler_type["message_class"], 'message_type': 'check_ram_usage',
                    'value': ram_usage_percentage}

    message_handler.add_message(message_json)

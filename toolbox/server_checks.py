import re
import subprocess
import sys


def check_disk_usage(message_handler, config_arguments):
    filesystem = config_arguments["filesystem"]
    output_string = subprocess.run(["df", "-h"], capture_output=True).stdout.decode("utf-8")
    match = re.search(filesystem, output_string)
    if match is None:
        return "SERVER STATUS CHECK FAILED! (df -h)"
    match = re.search("[0-9]*%", match[0])
    if match is None:
        return "SERVER STATUS CHECK FAILED! (df -h)"
    disk_usage_percentage = int(match[0][:-1])

    message_json = {'message_type': 'check_disk_usage', 'value': str(disk_usage_percentage)}

    message_handler.add_message(message_json)

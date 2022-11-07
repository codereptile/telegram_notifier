import re
import subprocess


def check_disk_usage(message_handler, **kwargs):
    output_string = subprocess.run(["df", "-h"], capture_output=True).stdout.decode("utf-8")
    match = re.search(kwargs.get("filesystem"), output_string)
    if match is None:
        return "SERVER STATUS CHECK FAILED! (df -h)"
    match = re.search("[0-9]*%", match[0])
    if match is None:
        return "SERVER STATUS CHECK FAILED! (df -h)"
    disk_usage_percentage = int(match[0][:-1])
    message_handler.add_message("Disk usage: " + str(disk_usage_percentage) + "%\n")

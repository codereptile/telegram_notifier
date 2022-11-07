import re
import subprocess

DEFAULT_DISK_USAGE_PERCENT_TRIGGER = 1
disk_usage_percent_trigger = DEFAULT_DISK_USAGE_PERCENT_TRIGGER

FILE_SYSTEM_NAME = "/dev/nvme0n1p2.*"


def check_disk_usage(message_handler):
    global disk_usage_percent_trigger

    output_message = ""
    output_string = subprocess.run(["df", "-h"], capture_output=True).stdout.decode("utf-8")
    match = re.search(FILE_SYSTEM_NAME, output_string)
    if match is None:
        return "SERVER STATUS CHECK FAILED! (df -h)"
    match = re.search("[0-9]*%", match[0])
    if match is None:
        return "SERVER STATUS CHECK FAILED! (df -h)"
    disk_usage_percentage = int(match[0][:-1])
    if disk_usage_percentage >= disk_usage_percent_trigger:
        disk_usage_percent_trigger = disk_usage_percentage + 1
        output_message += "Warning: disk usage reached " + str(disk_usage_percentage) + "%\n"
    elif disk_usage_percentage < DEFAULT_DISK_USAGE_PERCENT_TRIGGER:
        disk_usage_percent_trigger = DEFAULT_DISK_USAGE_PERCENT_TRIGGER

    if output_message:
        message_handler.add_message(output_message)

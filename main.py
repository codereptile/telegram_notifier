import asyncio
import re
import threading

import subprocess

new_messages = []

DEFAULT_DISK_USAGE_PERCENT_TRIGGER = 1
disk_usage_percent_trigger = DEFAULT_DISK_USAGE_PERCENT_TRIGGER

CHECK_SERVER_INTERVAL = 3
SEND_UPDATES_INTERVAL = 1

messages_mutex = threading.Lock()


async def check_server_status():
    global disk_usage_percent_trigger
    global new_messages
    while True:
        output_message = ""
        output_string = subprocess.run(["df", "-h"], capture_output=True).stdout.decode("utf-8")
        match = re.search("/dev/nvme0n1p5.*", output_string)
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
            new_messages.append(output_message)

        await asyncio.sleep(CHECK_SERVER_INTERVAL)


async def send_updates():
    global new_messages

    while True:
        messages_mutex.acquire()
        if len(new_messages) != 0:
            for message in new_messages:
                print(message)

        new_messages = []
        messages_mutex.release()
        await asyncio.sleep(SEND_UPDATES_INTERVAL)


async def main():
    sending_updates = asyncio.create_task(send_updates())
    checking_server_status = asyncio.create_task(check_server_status())
    while True:
        await checking_server_status
        await sending_updates

asyncio.run(main())
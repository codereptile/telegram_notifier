import asyncio
import re
import threading

import subprocess
import time
from multiprocessing import Process

new_messages = []

DEFAULT_DISK_USAGE_PERCENT_TRIGGER = 70
disk_usage_percent_trigger = DEFAULT_DISK_USAGE_PERCENT_TRIGGER

CHECK_SERVER_INTERVAL = 3
SEND_UPDATES_INTERVAL = 1

messages_mutex = threading.Lock()

FILE_SYSTEM_NAME = "/dev/nvme0n1p2.*"


async def check_server_status():
    global disk_usage_percent_trigger
    global new_messages
    while True:
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
            messages_mutex.acquire()
            new_messages.append(output_message)
            messages_mutex.release()
        time.sleep(CHECK_SERVER_INTERVAL)


def send_updates():
    global new_messages

    while True:
        messages_mutex.acquire()
        if len(new_messages) != 0:
            for message in new_messages:
                print(message)

        new_messages = []
        messages_mutex.release()
        print(2)
        time.sleep(SEND_UPDATES_INTERVAL)


class Task:
    process = Process

    def __init__(self, function):
        self.function = function

    def start(self):
        process = Process(target=self.function)
        process.start()

    def get_process(self):
        return self.process

    def end(self):
        self.process.close()


if __name__ == '__main__':
    print("Client starts")

    tasks = list()

    task1 = Task(check_server_status())
    task2 = Task(send_updates())
    task1.start()
    task2.start()
    tasks.append(task1)
    tasks.append(task2)
    for task in tasks:
        task.get_process().join()

    # wait_until_stop_signal()

    # GRACEFUL STOP
    for task in tasks:
        task.stop()
    print("Client stops now")

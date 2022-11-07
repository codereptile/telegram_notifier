import re
import signal
import threading
import subprocess
import time

new_messages = []
stop_all_threads = False

DEFAULT_DISK_USAGE_PERCENT_TRIGGER = 1
disk_usage_percent_trigger = DEFAULT_DISK_USAGE_PERCENT_TRIGGER

messages_mutex = threading.Lock()

FILE_SYSTEM_NAME = "/dev/nvme0n1p2.*"


def check_server_status():
    global disk_usage_percent_trigger
    global new_messages

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


def send_updates():
    global new_messages

    messages_mutex.acquire()
    if len(new_messages) != 0:
        for message in new_messages:
            print(message)

    new_messages = []
    messages_mutex.release()


class Task(threading.Thread):
    def __init__(self, target, sleep):
        def periodic_caller():
            while not stop_all_threads:
                target()
                time.sleep(sleep)

        super().__init__(target=periodic_caller)


def graceful_stop(*args):
    global stop_all_threads

    print("Client stop initialized")
    stop_all_threads = True


if __name__ == '__main__':
    print("Client starts")

    tasks = [
        Task(check_server_status, 1),
        Task(send_updates, 1)
    ]
    for task in tasks:
        task.start()

    signal.signal(signal.SIGINT, graceful_stop)
    signal.signal(signal.SIGTERM, graceful_stop)

    for task in tasks:
        task.join()
    print("Client stop finished")

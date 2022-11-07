import re
import signal
import socket
import threading
import subprocess
import time
import message_handler


def send_data(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("localhost", 10002))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        assert response == "Accepted"


message_handler = message_handler.MessageHandler(send_data)

DEFAULT_DISK_USAGE_PERCENT_TRIGGER = 1
disk_usage_percent_trigger = DEFAULT_DISK_USAGE_PERCENT_TRIGGER

FILE_SYSTEM_NAME = "/dev/nvme0n1p2.*"


def check_server_status():
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


class Task(threading.Thread):
    def __init__(self, target, sleep):
        def periodic_caller():
            while not stop_all_threads:
                target()
                time.sleep(sleep)

        super().__init__(target=periodic_caller)


stop_all_threads = False


def graceful_stop(*args):
    global stop_all_threads

    print("Client stop initialized")
    stop_all_threads = True


if __name__ == '__main__':
    print("Client starts")

    tasks = [
        Task(check_server_status, 1),
        Task(message_handler.flush_messages, 1)
    ]
    for task in tasks:
        task.start()

    signal.signal(signal.SIGINT, graceful_stop)
    signal.signal(signal.SIGTERM, graceful_stop)

    for task in tasks:
        task.join()
    print("Client stop finished")

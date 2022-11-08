import signal
import socket
import time
import message_handler
import server_checks
import background_task
import config_utils


CONFIG_NAME = "config.json"
CONFIG_DATA = config_utils.get_data_from_config(CONFIG_NAME)



def send_data(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("localhost", 10002))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        assert response == "Accepted"


message_handler = message_handler.MessageHandler(send_data)

if __name__ == '__main__':
    message_handler.send_immediately("Client 'test' online")

    task_pool = background_task.BackgroundTaskPool(message_handler)
    # add other tasks
    if config_utils.get_instrument_condition(CONFIG_DATA, "check_disk_usage"):
        filesystem = config_utils.get_instrument(CONFIG_DATA, "check_disk_usage")["filesystem"]
        sleep = config_utils.get_instrument_frequency(CONFIG_DATA, "check_disk_usage")
        task_pool.add_task(server_checks.check_disk_usage, sleep, filesystem=filesystem)
    # start tasks
    task_pool.start_tasks()

    signal.signal(signal.SIGINT, task_pool.graceful_stop)
    signal.signal(signal.SIGTERM, task_pool.graceful_stop)

    while task_pool.is_working:
        message_handler.flush_messages()
        time.sleep(0.1)

    task_pool.await_all_tasks()
    message_handler.send_immediately("Client 'test' offline")

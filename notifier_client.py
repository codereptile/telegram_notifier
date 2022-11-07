import signal
import socket
import time
import message_handler
import server_checks
import background_task


def send_data(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("localhost", 10002))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        assert response == "Accepted"


message_handler = message_handler.MessageHandler(send_data)

if __name__ == '__main__':
    print("Client starts")

    task_pool = background_task.BackgroundTaskPool(message_handler)
    task_pool.add_task(server_checks.check_disk_usage, 1)
    task_pool.start_tasks()

    signal.signal(signal.SIGINT, task_pool.graceful_stop)
    signal.signal(signal.SIGTERM, task_pool.graceful_stop)

    while not task_pool.get_stop_all_threads():
        message_handler.flush_messages()
        time.sleep(0.1)

    print("Client stop initialized")
    task_pool.await_all_tasks()
    print("Client stop finished")

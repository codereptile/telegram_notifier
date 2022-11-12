import json
import select
import signal
import socket
import sys
import time
from toolbox import background_task, message_handler, server_checks

CONFIG_NAME = "client_config.json"
config_data = json.load(open(CONFIG_NAME))


def send_data(message: dict):
    message["client_name"] = config_data["client_name"]

    if config_data["message_protocol"] == "server":
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((config_data["host"], config_data["port"]))
                sock.sendall(bytes(json.dumps(message), 'ascii'))
                response = str(sock.recv(1024), 'ascii')
                assert response == "Accepted"
        except Exception as e:
            print("Failed to send message: " + json.dumps(message), file=sys.stderr)
    else:
        print(json.dumps(message))


if __name__ == '__main__':
    message_handler = message_handler.MessageHandler(send_data)
    message_handler.send_immediately({'message_type': 'instant_message', 'value': "Client powering up"})

    task_pool = background_task.BackgroundTaskPool(message_handler)
    # add mandatory tasks
    task_pool.add_task_simple(message_handler.flush_messages, 0.1)
    # add optional tasks
    for i in config_data["tasks"]:
        if config_data["tasks"][i]["enable"] == 1:
            task_pool.add_task(getattr(server_checks, i), config_data["tasks"][i])
    # start tasks
    task_pool.start_tasks()

    signal.signal(signal.SIGINT, task_pool.graceful_stop)
    signal.signal(signal.SIGTERM, task_pool.graceful_stop)

    if config_data["supervisor_event_listener"] == 1:
        def write_stdout(s):
            sys.stdout.write(s)
            sys.stdout.flush()


        write_stdout('READY\n')  # transition from ACKNOWLEDGED to READY
        while task_pool.is_working:
            if select.select([sys.stdin, ], [], [], 0.0)[0]:
                header_line = ""
                while len(header_line) < 2:
                    header_line = sys.stdin.readline()
                header = dict([x.split(':') for x in header_line.split()])

                payload_line = sys.stdin.read(int(header['len']))
                payload = dict([x.split(':') for x in payload_line.split()])

                try:
                    message_json = {'message_type': 'supervisor_event_listener',
                                    'value': "Process: " + payload['processname'] + "\nEvent: " + header['eventname']}
                    message_handler.add_message(message_json)
                except Exception as e:
                    print(header_line + payload_line)
                write_stdout('RESULT 2\nOK')
                write_stdout('READY\n')  # transition from ACKNOWLEDGED to READY
            else:
                time.sleep(0.1)

    task_pool.await_all_tasks()
    message_handler.send_immediately({'message_type': 'instant_message', 'value': "Client powering down"})

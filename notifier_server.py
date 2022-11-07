import signal
import threading
import socketserver
import message_handler
import time
from telegram.ext import Updater

messages_mutex = threading.Lock()
file_mutex = threading.Lock()
new_messages = []
stop_all_threads = False
with open("token.txt") as file:
    TOKEN = file.read()
updater = Updater(TOKEN)


def print_update(bot, chat_id, message):
    bot.send_message(chat_id=chat_id, text=str(message))


def send_messages(message):
    global updater
    recipients = []

    file_mutex.acquire()
    with open("recipients.txt", "r") as myfile:
        for i in myfile.readlines():
            recipients.append(int(i))
    file_mutex.release()

    for chat_id in recipients:
        print_update(updater.bot, chat_id, message)


message_handler = message_handler.MessageHandler(send_messages)


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = str(self.request.recv(1024), 'ascii')
        message_handler.add_message(data)
        response = bytes("Accepted", 'ascii')
        self.request.sendall(response)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def graceful_stop(*args):
    global stop_all_threads
    stop_all_threads = True


if __name__ == "__main__":
    updater.start_polling()

    # Subnautica cyclops engine start reference
    message_handler.send_immediately("Notifier (v3.0) powering up")

    server = ThreadedTCPServer(("localhost", 10002), ThreadedTCPRequestHandler)
    with server:

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

        signal.signal(signal.SIGINT, graceful_stop)
        signal.signal(signal.SIGTERM, graceful_stop)

        while not stop_all_threads:
            message_handler.flush_messages()
            time.sleep(0.1)

        message_handler.send_immediately("Notifier powering down")

        updater.stop()
        server.shutdown()

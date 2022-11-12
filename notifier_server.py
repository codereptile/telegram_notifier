import json
import signal
import threading
import socketserver
from pathlib import Path

from telegram import Update

from toolbox import config_utils, message_handler
import time
from telegram.ext import Updater, CallbackContext, CommandHandler

CONFIG_NAME = "server_config.json"
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
    if config_data["message_protocol"] == "telegram":
        global updater
        recipients = []

        file_mutex.acquire()
        with open("recipients.txt", "r") as myfile:
            for i in myfile.readlines():
                recipients.append(int(i))
        file_mutex.release()

        for chat_id in recipients:
            print_update(updater.bot, chat_id, message)
    else:
        print(message)


message_handler = message_handler.MessageHandler(send_messages)


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = str(self.request.recv(1024), 'ascii')

        data_json = json.loads(data)
        if data_json["message_type"] == "instant_message":
            message_handler.add_message(
                "Got instant message from " + data_json["client_name"] + ": " + data_json["value"])
        else:
            print("UNKNOWN MESSAGE TYPE:" + data)

        response = bytes("Accepted", 'ascii')
        self.request.sendall(response)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, server_address, request_handler_class):
        self.allow_reuse_address = True
        super().__init__(server_address, request_handler_class)


def graceful_stop(*args):
    global stop_all_threads
    stop_all_threads = True


def bot_command_start(update: Update, context: CallbackContext):
    file_mutex.acquire()
    already_saved = False

    with open("recipients.txt", "r") as myfile:
        for i in myfile.readlines():
            if int(i) == update.message.chat_id:
                already_saved = True

    if not already_saved:
        with open("recipients.txt", "a") as myfile:
            myfile.write(str(update.message.chat_id) + "\n")
    file_mutex.release()

    if already_saved:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="You're already on the notification list!")
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Hi!\nYou're all set to receive notifications!")


if __name__ == "__main__":
    config_data = config_utils.load_config(CONFIG_NAME)

    recipients_filename = Path('recipients.txt')
    recipients_filename.touch(exist_ok=True)

    updater.start_polling()
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", bot_command_start))

    # Subnautica cyclops engine start reference
    message_handler.send_immediately("Notifier v3 powering up")

    server = ThreadedTCPServer((config_data["host"], config_data["port"]), ThreadedTCPRequestHandler)
    with server:
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        signal.signal(signal.SIGINT, graceful_stop)
        signal.signal(signal.SIGTERM, graceful_stop)

        while not stop_all_threads:
            message_handler.flush_messages()
            time.sleep(0.1)

        message_handler.send_immediately("Notifier powering down")

        updater.stop()
        server.shutdown()

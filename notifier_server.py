import json
import signal
import sys
import threading
import socketserver
from pathlib import Path

from telegram import Update

from toolbox import message_handler, client_handler, background_task
import time
from telegram.ext import Updater, CallbackContext, CommandHandler

CONFIG_NAME = "server_config.json"
messages_mutex = threading.Lock()
file_mutex = threading.Lock()
new_messages = []
stop_all_threads = False


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
        return "Accepted"
    else:
        print(message)
        return "Accepted"


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        answer_message = client_handler.process_message(message_handler, str(self.request.recv(1024), 'ascii'))
        response = bytes(answer_message, 'ascii')
        self.request.sendall(response)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, server_address, request_handler_class):
        self.allow_reuse_address = True
        super().__init__(server_address, request_handler_class)


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


def bot_command_status(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=client_handler.status())


if __name__ == "__main__":
    config_data = json.load(open(CONFIG_NAME))
    message_handler = message_handler.MessageHandler(send_messages)
    client_handler = client_handler.ClientHandler(config_data)
    client_handler.load_clients()

    if config_data["message_protocol"] == "telegram":
        recipients_filename = Path('recipients.txt')
        recipients_filename.touch(exist_ok=True)

        with open("token.txt") as file:
            TOKEN = file.readline().strip()
        updater = Updater(TOKEN)

        updater.start_polling()
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", bot_command_start))
        dispatcher.add_handler(CommandHandler("status", bot_command_status))

    # Subnautica cyclops engine start reference
    message_handler.send_immediately("Notifier v3 powering up")

    task_pool = background_task.BackgroundTaskPool(message_handler)
    # add mandatory tasks
    task_pool.add_task_simple(message_handler.flush_messages, 0.1)
    task_pool.add_task_simple(client_handler.check_clients, 0.1, message_handler=message_handler)
    # start tasks
    task_pool.start_tasks()

    server = ThreadedTCPServer((config_data["host"], config_data["port"]), ThreadedTCPRequestHandler)
    with server:
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        signal.signal(signal.SIGINT, task_pool.graceful_stop)
        signal.signal(signal.SIGTERM, task_pool.graceful_stop)

        while task_pool.is_working:
            time.sleep(0.1)

        message_handler.send_immediately("Notifier powering down")

        if config_data["message_protocol"] == "telegram":
            updater.stop()

        server.shutdown()

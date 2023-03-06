import threading


class MessageHandler:
    def __init__(self, send_cb):
        self.send_cb = send_cb
        self.messages_lock = threading.Lock()
        self.message_pool = []

    def add_message(self, message):
        self.messages_lock.acquire()
        self.message_pool.append(message)
        self.messages_lock.release()

    def flush_messages(self):
        self.messages_lock.acquire()
        for message in self.message_pool:
            try:
                self.send_cb(message)
                self.message_pool.remove(message)
            except Exception as e:
                pass
        self.messages_lock.release()

    def send_immediately(self, message):
        self.send_cb(message)

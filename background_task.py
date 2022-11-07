import threading
import time

stop_all_threads = False


class BackgroundTask(threading.Thread):
    def __init__(self, target, sleep, message_handler):
        def periodic_caller():
            while not stop_all_threads:
                target(message_handler)
                time.sleep(sleep)

        super().__init__(target=periodic_caller)


class BackgroundTaskPool:
    def __init__(self, message_handler):
        self.message_handler = message_handler
        self.task_pool = []

    def add_task(self, target, sleep):
        self.task_pool.append(BackgroundTask(target, sleep, self.message_handler))

    def start_tasks(self):
        for task in self.task_pool:
            task.start()

    @staticmethod
    def graceful_stop(*args):
        global stop_all_threads
        stop_all_threads = True

    @staticmethod
    def get_stop_all_threads():
        global stop_all_threads
        return stop_all_threads

    def await_all_tasks(self):
        for task in self.task_pool:
            task.join()

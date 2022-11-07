import threading
import time


class BackgroundTask(threading.Thread):
    def __init__(self, target, sleep, message_handler):
        self.stop_thread = False

        def periodic_caller():
            while not self.stop_thread:
                target(message_handler)
                time.sleep(sleep)

        super().__init__(target=periodic_caller)

    def stop(self):
        self.stop_thread = True


class BackgroundTaskPool:
    def __init__(self, message_handler):
        self.message_handler = message_handler
        self.is_working = True
        self.task_pool = []

    def add_task(self, target, sleep):
        self.task_pool.append(BackgroundTask(target, sleep, self.message_handler))

    def start_tasks(self):
        for task in self.task_pool:
            task.start()

    def graceful_stop(self, *args):
        for task in self.task_pool:
            task.stop()
        self.is_working = False

    def await_all_tasks(self):
        for task in self.task_pool:
            task.join()

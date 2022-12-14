import threading
import time


class BackgroundTaskSimple(threading.Thread):
    def __init__(self, target, period, **kwargs):
        self.stop_thread = False
        self.sleep = period

        def periodic_caller():
            while not self.stop_thread:
                target(**kwargs)
                time.sleep(self.sleep)

        super().__init__(target=periodic_caller)

    def stop(self):
        self.stop_thread = True


class BackgroundTask(threading.Thread):
    def __init__(self, target, message_handler, task_config):
        self.stop_thread = False
        self.sleep = task_config["period"]

        def periodic_caller():
            while not self.stop_thread:
                target(message_handler, task_config["arguments"])
                time.sleep(self.sleep)

        super().__init__(target=periodic_caller)

    def stop(self):
        self.stop_thread = True


class BackgroundTaskPool:
    def __init__(self, message_handler):
        self.message_handler = message_handler
        self.is_working = True
        self.task_pool = []

    def add_task(self, target, task_data):
        self.task_pool.append(BackgroundTask(target, self.message_handler, task_data))

    def add_task_simple(self, target, period, **kwargs):
        self.task_pool.append(BackgroundTaskSimple(target, period, **kwargs))

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

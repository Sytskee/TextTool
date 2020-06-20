from datetime import datetime


class ExecutorBase:
    def __init__(self, data_files_path, output_path, status_report_queue=None):
        self.data_files_path = data_files_path
        self.output_path = output_path
        self.status_report_queue = status_report_queue

        self.load_data()

    def load_data(self):
        raise NotImplementedError("Please implement this method")

    def report_status(self, message):
        if self.status_report_queue is not None:
            self.status_report_queue.put('{} -> {}'.format(datetime.now().strftime('%H:%M:%S'), message))
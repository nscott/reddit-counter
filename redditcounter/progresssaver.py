from Queue import Queue
import json

class ProgressSaver:
    """Serializes whatever is on its queue as JSON and writes to a file on regular intervals"""
    def __init__(self):
        self.queue = Queue(maxsize=10000)

    def write_out(self, file_name):
        # 'a' is append mode
        with open(file_name, 'a') as f:
            # dequeue until empty
            while not self.queue.empty():
                queue_item = self.queue.get_nowait()
                f.write(json.dumps(queue_item))
                f.write(',\n')

    def add_record(self, item):
        self.queue.put_nowait(item)

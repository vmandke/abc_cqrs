from multiprocessing.connection import Connection
import sys


class Actor:
    def __init__(self, in_queue=None):
        self.in_queue = in_queue
        self.behaviour = {}

    def set_in_queue(self, in_queue):
        self.in_queue = in_queue

    def get_in_queue(self):
        return self.in_queue

    def register_receive(self, command, command_fn):
        self.behaviour[command] = command_fn

    @staticmethod
    def non_blocking_get(pipe):
        result = None
        try:
            result = (
                (pipe.recv() if pipe.poll() else None) if isinstance(pipe, Connection) else pipe.get(False)
            )
        except Exception:
            pass
        return result

    def blocking_get(self):
        return (
            self.in_queue.recv() if isinstance(self.in_queue, Connection) else self.in_queue.get()
        )

    @staticmethod
    def put_on_sender(result, sender_queue):
        (
            sender_queue.send(result) if isinstance(sender_queue, Connection) else sender_queue.put(result)
        )

    def receive(self):
        # Receive the command from queue
        # and execute associated function
        command, sender_queue, args = self.blocking_get()
        if command == 'exit':
            sys.exit()
        else:
            fn = self.behaviour[command]
            result = fn() if not args else fn(**args)
            if sender_queue:
                self.put_on_sender(result, sender_queue)

    def start(self):
        while True:
            self.receive()

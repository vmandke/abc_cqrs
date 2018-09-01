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

    def receive(self):
        # Receive the command from queue
        # and execute associated function
        command, sender_queue, args = self.in_queue.get()
        if command == 'exit':
            sys.exit()
        else:
            fn = self.behaviour[command]
            result = fn() if not args else fn(**args)
            if sender_queue:
                sender_queue.put(result)

    def start(self):
        while True:
            self.receive()

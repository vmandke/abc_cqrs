import queue
import threading
import time

from parkinglot.util.registry import Registry
from parkinglot.util.actor import Actor

class AdditionActor(Actor):
    def __init__(self, in_queue):
        super().__init__(in_queue)
        self.register_receive('add', self.add)
    def add(self, x, y):
        return x + y

def test_addition_actor():
    in_queue = queue.Queue()
    sender_queue = queue.Queue()
    add_actor = AdditionActor(in_queue)
    in_queue.put(('add', sender_queue, {'x': 1, 'y': 2}))
    # force receive
    add_actor.receive()
    assert(sender_queue.get() == 3)


def test_registry():
    registry_in_queue = queue.Queue()
    assert(threading.active_count() == 1)
    test_registry = Registry('test', registry_in_queue)
    registry_in_queue.put(('spawn', None, {'identifier': 'adder',
                                           'actor_type': AdditionActor}))
    test_registry.receive()
    time.sleep(1)
    assert(threading.active_count() == 2)
    sender_queue = queue.Queue()
    registry_in_queue.put(('ask_foward',
                           None,
                           {'identifier': 'adder',
                            'command': 'add',
                            'sender_queue': sender_queue,
                            'command_args': {'x': 1, 'y': 2}}))
    test_registry.receive()
    assert(sender_queue.get() == 3)
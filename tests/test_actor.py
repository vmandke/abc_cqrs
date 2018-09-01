import queue
import threading
import time

from parkinglot.util.actor import Actor

def create_addition_actor(in_queue):
    add_actor = Actor(in_queue)
    add_actor.register_receive('add', lambda x,y: x + y)
    return add_actor

def test_simple_actor():
    # Create in_queue, and sender queues
    in_queue = queue.Queue()
    sender_queue = queue.Queue()
    # Initialize the add_actor
    add_actor = create_addition_actor(in_queue)
    # Put command on queue
    in_queue.put(('add', sender_queue, {'x': 1, 'y': 2}))
    # force actor to work once
    add_actor.receive()
    # Check that response it got from actor
    response = sender_queue.get()
    assert(response == 3)

def test_actor_in_own_context():
    def context(in_queue):
        add_actor = create_addition_actor(in_queue)
        add_actor.start()
    assert(threading.active_count() == 1)
    in_queue = queue.Queue()
    sender_queue = queue.Queue()
    thread_ = threading.Thread(name='testactor',
                               target=context,
                               args=(in_queue,))
    thread_.daemon = True
    thread_.start()
    assert(threading.active_count() == 2)
    in_queue.put(('exit', None, None))
    # Wait sometime for the command to be read
    time.sleep(2)
    assert(threading.active_count() == 1)



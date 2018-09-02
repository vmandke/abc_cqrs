import threading
import queue

from parkinglot.util import Actor

def actor_context(actor_type, actor_args):
    actor = actor_type(**actor_args)
    actor.start()

class Registry(Actor):
    def __init__(self, name, in_queue):
        self.name = name
        self.registered = {}
        super().__init__(in_queue)
        self.register_receive('spawn', self.spawn)
        self.register_receive('ask_foward', self.ask_foward)
        self.register_receive('kill_actor', self.kill_actor)

    def spawn(self, identifier, actor_type, actor_args):
        in_queue = queue.Queue()
        actor_args['in_queue'] = in_queue
        actor_thread = threading.Thread(name=identifier,
                                        target=actor_context,
                                        args=(actor_type, actor_args))
        actor_thread.daemon = True
        actor_thread.start()
        self.registered[identifier] = {
            'id': identifier,
            'in_queue': in_queue,
            'context': actor_thread
        }

    def ask_foward(self, identifier, command, sender_queue, command_args):
        # Put a command on the in_queue of the identified actor
        self.registered[identifier]['in_queue'].put((
            command, sender_queue, command_args))

    def kill_actor(self, identifier):
        # Individual actors should handle this poison pill
        self.registered[identifier]['in_queue'].put(('exit', None, None))

from multiprocessing.connection import Connection

class CommandExecuter():
    def __init__(self, read_registry_queue, write_registry_queue):
        self.commands = {}
        self.queries = {}
        self.registry_commands = {}
        self.read_registry_queue = read_registry_queue
        self.write_registry_queue = write_registry_queue

    def add_query(self, command, arg_count, arg_names):
        self.queries[command] = (arg_count, arg_names)

    def add_command(self, command, arg_count, arg_names):
        self.commands[command] = (arg_count, arg_names)

    def add_registry_command(self, command, arg_count, arg_names, registry_fn):
        self.registry_commands[command] = (arg_count, arg_names, registry_fn)

    def get_command_args_and_id(self, command_line, arg_count, arg_names):
        identifier = "0" # set the default identifier
        if len(command_line) == arg_count + 2:
            identifier = command_line[-1]
        command_args = dict(zip(arg_names, command_line[1:1 + len(arg_names)]))
        return identifier, command_args

    def send_to_sender(self, sender_queue, event):
        (sender_queue.send(event)
         if isinstance(sender_queue, Connection)
         else sender_queue.put(event))

    def execute_command_line(self, command_line, sender_queue):
        command_line = list(filter(lambda x: x, command_line.split(' ')))
        command = command_line[0]
        arg_count, arg_names = None, None
        if command in self.registry_commands:
            arg_count, arg_names, registry_fn = self.registry_commands[command]
            identifier, command_args = self.get_command_args_and_id(
                                            command_line, arg_count, arg_names)
            command_args['sender_conn'] = sender_queue
            registry_fn(**command_args)
        elif command in self.queries:
            arg_count, arg_names = self.queries[command]
            identifier, command_args = self.get_command_args_and_id(
                                            command_line, arg_count, arg_names)

            self.read_registry_queue.put((
                'ask_foward', None,
                {'identifier': identifier,
                 'sender_queue': sender_queue,
                 'command': command,
                 'command_args': command_args}))
        elif command in self.commands:
            arg_count, arg_names = self.commands[command]
            identifier, command_args = self.get_command_args_and_id(
                                            command_line, arg_count, arg_names)
            self.write_registry_queue.put((
                'ask_foward', None,
                {'identifier': identifier,
                 'sender_queue': sender_queue,
                 'command': command,
                 'command_args': command_args}))
        else:
            if sender_queue:
                self.send_to_sender(
                    sender_queue, '{} is not a registered command'.format(command))

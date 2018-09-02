import queue
from parkinglot.user.parser import CommandExecuter

def test_command_executer():
    read_registry_queue = queue.Queue()
    write_registry_queue = queue.Queue()
    sender_queue = queue.Queue()
    test_parser = CommandExecuter(read_registry_queue, write_registry_queue)
    # register a registry command
    test_parser.add_registry_command('reg_comm', 1, ['arg1'])
    test_parser.execute_command_line(
        'reg_comm arg1_value', sender_queue)
    # Ensure the command is passed on read/ write queues
    assert(read_registry_queue.get() == ('reg_comm', None, {'arg1': 'arg1_value'}))
    assert(write_registry_queue.get() == ('reg_comm', None, {'arg1': 'arg1_value'}))
    # register a command
    test_parser.add_command('add_save', 2, ['x', 'y'])
    test_parser.execute_command_line(
        'add_save 3 4', sender_queue)
    assert(write_registry_queue.get() == (
                'add_save', None, {'command_args': {'y': '4', 'x': '3'}, 
                                   'identifier': '1', 
                                   'command': 'add_save', 
                                   'sender_queue': sender_queue}))
    # register a query
    test_parser.add_query('add_get', 2, ['x', 'y'])
    test_parser.execute_command_line(
        'add_get 3 4 2', sender_queue)
    assert(read_registry_queue.get() == (
                'add_get', None, {'command_args': {'y': '4', 'x': '3'}, 
                                   'identifier': '2', 
                                   'command': 'add_get', 
                                   'sender_queue': sender_queue}))
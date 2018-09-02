import multiprocessing as mp
import queue
import time

from parkinglot.user.parser import CommandExecuter
from parkinglot.util.passablequeue import MultiProcessPassableQueue
from parkinglot.writeside.registry import (
    ParkingLotRegistry as WriteSideRegistry)
from parkinglot.readside.registry import ParkingLotRegistry as ReadSideRegistry
from parkinglot.util.car import Car


def test_command_executer():
    read_registry_queue = queue.Queue()
    write_registry_queue = queue.Queue()
    sender_queue = queue.Queue()
    test_parser = CommandExecuter(read_registry_queue, write_registry_queue)
    # register a registry command

    def reg_comm_fn(arg1, sender_conn):
        read_registry_queue.put(('reg_comm', None, {'arg1': 'arg1_value'}))
        write_registry_queue.put(('reg_comm', None, {'arg1': 'arg1_value'}))
    test_parser.add_registry_command('reg_comm', 1, ['arg1'], reg_comm_fn)
    test_parser.execute_command_line(
        'reg_comm arg1_value', sender_queue)
    # Ensure the command is passed on read/ write queues
    assert(read_registry_queue.get() == ('reg_comm',
                                         None,
                                         {'arg1': 'arg1_value'}))
    assert(write_registry_queue.get() == ('reg_comm',
                                          None,
                                          {'arg1': 'arg1_value'}))
    # register a command
    test_parser.add_command('add_save', 2, ['x', 'y'])
    test_parser.execute_command_line(
        'add_save 3 4', sender_queue)
    assert(write_registry_queue.get() == (
                'ask_foward', None, {'command_args': {'y': '4', 'x': '3'},
                                     'identifier': '0',
                                     'command': 'add_save',
                                     'sender_queue': sender_queue}))
    # register a query
    test_parser.add_query('add_get', 2, ['x', 'y'])
    test_parser.execute_command_line(
        'add_get 3 4 2', sender_queue)
    assert(read_registry_queue.get() == (
                'ask_foward', None, {'command_args': {'y': '4', 'x': '3'},
                                     'identifier': '2',
                                     'command': 'add_get',
                                     'sender_queue': sender_queue}))


def test_executer_multiprocess():
    process_manager = mp.Manager()

    def writeworker(registry_type, in_queue, read_queue):
        registry = registry_type(in_queue, read_queue)
        registry.start()

    def readworker(registry_type, in_queue):
        registry = registry_type(in_queue)
        registry.start()

    write_queue = process_manager.Queue()
    read_queue = process_manager.Queue()
    write_registry = mp.Process(target=writeworker, args=(WriteSideRegistry,
                                                          write_queue,
                                                          read_queue))
    write_registry.start()
    read_registry = mp.Process(target=readworker, args=(ReadSideRegistry,
                                                        read_queue))
    read_registry.start()
    test_parser = CommandExecuter(read_queue, write_queue)
    time.sleep(1)

    def create_parking(num_slots, sender_conn):
        write_queue.put(('create_parking_lot', None,
                         {'num_slots': num_slots,
                          'sender_conn': sender_conn}))

    test_parser.add_registry_command(
        'create_parking_lot', 1, ['num_slots'], create_parking)
    test_parser.execute_command_line(
        'create_parking_lot 6', None)
    # Park a car
    time.sleep(1)
    write_queue.put(('ask_foward',
                     None,
                     {'identifier': '0',
                      'command': 'park',
                      'sender_queue': None,
                      'command_args': {'rno': '1', 'color': 'White'}}))
    time.sleep(2)
    # # Receive status
    piped_queue = MultiProcessPassableQueue()
    read_queue.put(('ask_foward',
                    None,
                    {'identifier': '0',
                     'command': 'status',
                     'sender_queue': piped_queue.get_producer_conn(),
                     'command_args': {}}))
    expected_status = ('Slot No. Registration No Colour\n' +
                       '1        1               White ')
    assert(piped_queue.get_consumer_conn().recv() == expected_status)
    write_queue.put(('exit', None, None))
    read_queue.put(('exit', None, None))
    time.sleep(2)
    write_registry.join(timeout=1)
    read_registry.join(timeout=1)

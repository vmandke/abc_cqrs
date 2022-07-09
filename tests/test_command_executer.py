import multiprocessing as mp
import queue
import time
from functools import partial

import parkinglot
from parkinglot.user.parser import CommandExecuter
from parkinglot.util.passablequeue import MultiProcessPassableQueue
from parkinglot.writeside.registry import ParkingLotRegistry as WriteSideRegistry
from parkinglot.readside.registry import ParkingLotRegistry as ReadSideRegistry


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
    write_queue = mp.Queue()
    read_queue = mp.Queue()

    read_registry = mp.Process(target=partial(ReadSideRegistry, read_queue, auto_start=True))
    read_registry.start()
    write_registry = mp.Process(target=partial(WriteSideRegistry, write_queue, read_queue, auto_start=True))
    write_registry.start()
    test_parser = CommandExecuter(read_queue, write_queue)
    time.sleep(1)

    def create_parking(num_slots, name, sender_conn):
        write_queue.put(
            ('create_parking_lot', None, {'num_slots': num_slots, 'name': name, 'sender_conn': sender_conn})
        )

    test_parser.add_registry_command('create_parking_lot', 2, ['num_slots', 'name'], create_parking)
    test_parser.execute_command_line('create_parking_lot 6 Lot1', None)
    # Park a car
    time.sleep(1)
    write_queue.put(('ask_foward',
                     None,
                     {'identifier': 'Lot1',
                      'command': 'park',
                      'sender_queue': None,
                      'command_args': {'rno': '1', 'color': 'White'}}))
    time.sleep(2)
    # # Receive status
    conn1, conn2 = mp.Pipe(True)
    read_queue.put(
        ('ask_foward', None, {'identifier': 'Lot1', 'command': 'status', 'sender_queue': conn1, 'command_args': {}})
    )
    expected_status = ('Slot No. Registration No Colour\n' +
                       '1        1               White ')
    time.sleep(2)
    assert conn2.poll()
    assert conn2.recv() == expected_status
    write_queue.put(('exit', None, None))
    read_queue.put(('exit', None, None))
    time.sleep(2)
    write_registry.join(timeout=1)
    read_registry.join(timeout=1)

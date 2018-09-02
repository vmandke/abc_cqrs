import multiprocessing as mp
import sys
import os.path

from parkinglot.user.parser import CommandExecuter
from parkinglot.writeside.registry import ParkingLotRegistry as WriteSideRegistry
from parkinglot.readside.registry import ParkingLotRegistry as ReadSideRegistry
from parkinglot.util.passablequeue import MultiProcessPassableQueue

class Runner():
    def __init__(self):
        self.manager = mp.Manager()
        self.read_queue = self.manager.Queue()
        self.write_queue = self.manager.Queue()
        self.command_parser = CommandExecuter(self.read_queue,
                                              self.write_queue)
        # Create a write side register
        self.write_registry = mp.Process(
            target=self.register, args=(WriteSideRegistry,
                                        self.write_queue,
                                        self.read_queue))
        # Create a read side register
        self.read_registry = mp.Process(
            target=self.register, args=(ReadSideRegistry,
                                        self.read_queue))
        self.write_registry.start()
        self.read_registry.start()
        self.register_commands()

    def register(self, registry_type, in_queue, read_queue=None):
        if read_queue:
            registry = registry_type(in_queue, read_queue)
        else:
            registry = registry_type(in_queue)
        registry.start()

    def create_parking_lot(self, num_slots, sender_conn):
        self.write_queue.put(('create_parking_lot', None,
                             {'num_slots': num_slots,
                              'sender_conn': sender_conn}))

    def exit(self, sender_conn):
        self.write_queue.put(('exit', None, None))
        self.read_queue.put(('exit', None, None))
        self.write_registry.terminate()
        self.read_registry.terminate()
        sys.exit()

    def register_commands(self):
        self.command_parser.add_registry_command(
            'create_parking_lot', 1, ['num_slots'], self.create_parking_lot)
        self.command_parser.add_registry_command(
            'exit', 0, [], self.exit)
        self.command_parser.add_command('park', 2, ['rno', 'color'])
        self.command_parser.add_command('leave', 1, ['slot'])
        self.command_parser.add_query('status', 0, [])
        self.command_parser.add_query(
            'registration_numbers_for_cars_with_colour', 1, ['color'])
        self.command_parser.add_query(
            'slot_numbers_for_cars_with_colour', 1, ['color'])
        self.command_parser.add_query(
            'slot_number_for_registration_number', 1, ['rno'])

    def read_command_line(self):
        piped_queue = MultiProcessPassableQueue()
        self.command_parser.execute_command_line(
            input(), piped_queue.get_producer_conn())
        print(piped_queue.get_consumer_conn().recv())

    def run_from_file(self, filename):
        with open(filename, 'r') as fd:
            for line in fd:
                piped_queue = MultiProcessPassableQueue()
                self.command_parser.execute_command_line(
                    line, piped_queue.get_producer_conn())
                print(piped_queue.get_consumer_conn().recv())

def run():
    runner = Runner()
    while True:
        if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
            runner.run_from_file(sys.argv[1])
        runner.read_command_line()


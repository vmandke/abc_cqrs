from parkinglot.util.registry import Registry
from parkinglot.writeside.lot import WriteSideLot
from parkinglot.util.passablequeue import MultiProcessPassableQueue


class ParkingLotRegistry(Registry):
    def __init__(self, in_queue, read_registry_queue, auto_start=False):
        super().__init__('WriteSideParkingRegistry', in_queue)
        self.num_lots = 0
        self.read_registry_queue = read_registry_queue
        self.register_receive('create_parking_lot', self.create_parking_lot)
        if auto_start:
            self.start()

    def create_parking_lot(self, name, num_slots, sender_conn):
        # trigger a actor spwan
        piped_queue = MultiProcessPassableQueue()
        args = {'name': name, 'num_slots': num_slots,
                'read_side_events': piped_queue.get_producer_conn(),
                'sender_conn': sender_conn}
        self.in_queue.put(('spawn', None, {'identifier': name,
                                           'actor_type': WriteSideLot,
                                           'actor_args': args}))
        self.read_registry_queue.put((
            'create_parking_lot', None,
            {'num_slots': num_slots, 'name': name, 'read_events_queue': piped_queue.get_consumer_conn()}
        ))

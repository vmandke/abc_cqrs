from parkinglot.util.registry import Registry
from parkinglot.writeside.lot import WriteSideLot
from parkinglot.util.passablequeue import MultiProcessPassableQueue

class ParkingLotRegistry(Registry):
    def __init__(self, in_queue, read_registry_queue):
        super().__init__('WriteSideParkingRegistry', in_queue)
        self.num_lots = 0
        self.read_registry_queue = read_registry_queue
        self.register_receive('create_parking_lot', self.create_parking_lot)

    def create_parking_lot(self, num_slots):
        # trigger a actor spwan
        lotid = str(self.num_lots)
        piped_queue = MultiProcessPassableQueue()
        args = {'name': lotid, 'num_slots': num_slots,
                'read_side_events': piped_queue.get_producer_conn()}
        self.in_queue.put(('spawn', None, {'identifier': lotid,
                                           'actor_type': WriteSideLot,
                                           'actor_args': args}))
        self.read_registry_queue.put((
            'create_parking_lot', None,
            {'num_slots': num_slots,
             'read_events_queue': piped_queue.get_consumer_conn()}))

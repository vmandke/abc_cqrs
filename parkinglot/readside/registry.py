from parkinglot.util.registry import Registry
from parkinglot.readside.lot import ReadSideLot


class ParkingLotRegistry(Registry):
    def __init__(self, in_queue, auto_start=False):
        super().__init__('ReadSideParkingRegistry', in_queue)
        self.num_lots = 0
        self.register_receive('create_parking_lot', self.create_parking_lot)
        if auto_start:
            self.start()

    def create_parking_lot(self, name, num_slots, read_events_queue):
        # trigger a actor spwan
        args = {'name': name,  'num_slots': num_slots, 'writer_conn': read_events_queue}
        self.in_queue.put(('spawn', None, {'identifier': name, 'actor_type': ReadSideLot, 'actor_args': args}))

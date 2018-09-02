from parkinglot.util.registry import Registry
from parkinglot.readside.lot import ReadSideLot


class ParkingLotRegistry(Registry):
    def __init__(self, in_queue):
        super().__init__('ReadSideParkingRegistry', in_queue)
        self.num_lots = 0
        self.register_receive('create_parking_lot', self.create_parking_lot)

    def create_parking_lot(self, num_slots, read_events_queue):
        # trigger a actor spwan
        lotid = str(self.num_lots)
        args = {'name': lotid,
                'num_slots': num_slots,
                'writer_conn': read_events_queue}
        self.in_queue.put(('spawn', None, {'identifier': lotid,
                                           'actor_type': ReadSideLot,
                                           'actor_args': args}))

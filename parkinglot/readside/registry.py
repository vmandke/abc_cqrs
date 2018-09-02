from parkinglot.util.registry import Registry
from parkinglot.readside.lot import ReadSideLot

class ParkingLotRegistry(Registry):
    def __init__(self, name, in_queue):
        super().__init__('ReadSideParkingRegistry', in_queue)
        self.num_lots = 0
        self.lot_type = lot_type
        self.register_receive('create_parking_lot', self.create_parking_lot)

    def create_parking_lot(self, num_slots):
        # trigger a actor spwan
        lotid = str(self.num_slots)
        args = {'name': lotid, 'num_slots': num_slots}
        self.in_queue.put(('spwan', None, {'identifier': lotid,
                                           'actor_type': WriteSideLot,
                                           'actor_args': args}))

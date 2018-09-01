import bisect

from parkinglot.util.actor import Actor

class WriteSideLot(Actor):
    def __init__(self, name, num_slots, in_queue, read_side_events):
        super().__init__(in_queue)
        self.num_slots = num_slots
        # At the very beginning the very first
        # slot is empty
        self.empty = [i for i in range(1, num_slots + 1)]
        self.occupied = {}
        self.register_receive('park', self.park)
        self.register_receive('leave', self.leave)

    def park(self, car):
        result = "Sorry, parking lot is full"
        if len(self.empty) > 0:
            slot = self.empty.pop(0)
            self.occupied[slot] = car
            result = "Allocated slot number: {}".format(slot)
            read_side_events.put(('park', None, {'car': car, 'slot': slot}))
        return result

    def leave(self, slot):
        if slot in self.occupied:
            car = self.occupied.pop(slot)
            bisect.insort(self.empty, slot)
            read_side_events.put(('leave', None, {'slot': slot, 'car': car}))
        result = "Slot number {} is free".format(slot)

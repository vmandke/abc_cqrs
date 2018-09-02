import bisect
from multiprocessing.connection import Connection

from parkinglot.util.actor import Actor
from parkinglot.util.car import Car

class WriteSideLot(Actor):
    def __init__(self, name, num_slots, in_queue, read_side_events, sender_conn):
        super().__init__(in_queue)
        self.name = name
        self.read_side_events = read_side_events
        self.num_slots = int(num_slots)
        # At the very beginning the very first
        # slot is empty
        self.empty = [i for i in range(1, self.num_slots + 1)]
        self.occupied = {}
        self.register_receive('park', self.park)
        self.register_receive('leave', self.leave)
        if sender_conn:
            sender_conn.send(
                'Created a parking lot with {} slots'.format(self.num_slots))

    def send_read_side_event(self, event):
        (self.read_side_events.send(event)
         if isinstance(self.read_side_events, Connection)
         else self.read_side_events.put(event))

    def park(self, rno, color):
        car = Car(rno, color)
        result = "Sorry, parking lot is full"
        if len(self.empty) > 0:
            slot = self.empty.pop(0)
            self.occupied[slot] = car
            result = "Allocated slot number: {}".format(slot)
            self.send_read_side_event((
                'park', None, {'car': car, 'slot': slot}))
        return result

    def leave(self, slot):
        result = 'Slot number {} is free'.format(slot)
        slot = int(slot)
        if slot in self.occupied:
            car = self.occupied.pop(slot)
            bisect.insort(self.empty, slot)
            self.send_read_side_event((
                'leave', None, {'car': car, 'slot': slot}))
        elif slot < 1 or slot > self.num_slots:
            result = 'No such slot in the parking lot'
        return result

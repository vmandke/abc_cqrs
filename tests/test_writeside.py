import queue
import random

from parkinglot.writeside.lot import WriteSideLot
from parkinglot.util.car import Car


def fill_lot(max_slots, writelot, in_queue, sender_queue, events_queue):
    for slot in range(1, max_slots + 1):
        car = Car(str(slot), 'White')
        in_queue.put(('park', sender_queue,
                      {'rno': str(slot), 'color': 'White'}))
        writelot.receive()
        assert(sender_queue.get() == 'Allocated slot number: {}'.format(slot))
        events_response = events_queue.get()
        assert(events_response[0] == 'park')
        assert(events_response[1] is None)
        assert(events_response[2]['slot'] == slot)
    in_queue.put(('park', sender_queue, {'rno': str(max_slots + 1),
                                         'color': 'White'}))
    writelot.receive()
    assert(sender_queue.get() == 'Sorry, parking lot is full')


def leave(writelot, in_queue, sender_queue, events_queue):
    slot = random.choice(list(writelot.occupied.keys()))
    car = writelot.occupied[slot]
    in_queue.put(('leave', sender_queue, {'slot': slot}))
    writelot.receive()
    assert(sender_queue.get() == 'Slot number {} is free'.format(slot))
    assert(events_queue.get() == ('leave', None, {'car': car, 'slot': slot}))
    # Leave from a non existant slot
    in_queue.put(('leave', sender_queue, {'slot': -1}))
    writelot.receive()
    assert(sender_queue.get() == 'No such slot in the parking lot')


def test_writesidelot():
    in_queue = queue.Queue()
    events_queue = queue.Queue()
    sender_queue = queue.Queue()
    max_slots = 6
    writelot = WriteSideLot('test', max_slots, in_queue, events_queue, None)
    assert(len(writelot.empty) == max_slots)
    fill_lot(max_slots, writelot, in_queue, sender_queue, events_queue)
    leave(writelot, in_queue, sender_queue, events_queue)

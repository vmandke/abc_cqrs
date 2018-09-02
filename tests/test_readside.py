import queue
import random

from parkinglot.readside.lot import ReadSideLot
from parkinglot.util.car import Car

def fill_park(max_slots, in_queue, readlot):
    for slot in range(1, max_slots + 1):
        car = Car(str(slot), 'White')
        in_queue.put(('park', None, {'car': car, 'slot': slot}))
        readlot.receive()

def check_count(command, args, readlot, in_queue, sender_queue, expected_count):
    in_queue.put((command, sender_queue, args))
    readlot.receive()
    assert(len(str(sender_queue.get()).split(',')) == expected_count)


def test_readsidelot():
    in_queue = queue.Queue()
    sender_queue = queue.Queue()
    max_slots = 6
    readlot = ReadSideLot('test', max_slots, in_queue)
    # Check park
    fill_park(max_slots, in_queue, readlot)
    assert(len(readlot.registration_view) == max_slots)
    # Check getters
    # status
    in_queue.put(('status', sender_queue, None))
    readlot.receive()
    expected_status = '\n'.join([
        'Slot No. Registration No Colour',
        '1        1               White ',
        '2        2               White ',
        '3        3               White ',
        '4        4               White ',
        '5        5               White ',
        '6        6               White '])
    response_status = sender_queue.get()
    assert(response_status == expected_status)
    # Check leave
    cdata = readlot.registration_view[random.choice(
                list(readlot.registration_view.keys()))]
    in_queue.put(('leave', None,
                 {'car': cdata['car'], 'slot': cdata['slot']}))
    readlot.receive()
    assert(len(readlot.registration_view) == max_slots - 1)
    # registration_numbers_for_cars_with_colour
    check_count('registration_numbers_for_cars_with_colour', 
                {'color': 'White'},
                readlot,
                in_queue,
                sender_queue,
                max_slots - 1)
    # slot_numbers_for_cars_with_colour
    check_count('slot_numbers_for_cars_with_colour', 
                {'color': 'White'},
                readlot,
                in_queue,
                sender_queue,
                max_slots - 1)
    # slot_number_for_registration_number
    check_count('slot_number_for_registration_number', 
                {'rno': random.choice(list(readlot.registration_view.keys()))},
                readlot,
                in_queue,
                sender_queue,
                1)
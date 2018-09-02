from collections import defaultdict

from parkinglot.util.actor import Actor

class ReadSideLot(Actor):
    def __init__(self, name, num_slots, in_queue, writer_conn):
        super().__init__(in_queue)
        self.name = name
        self.registration_view = {}
        self.writer_conn = writer_conn
        self.color_view = defaultdict(lambda: [])
        self.register_receive('park', self.park)
        self.register_receive('leave', self.leave)
        self.register_receive('status', self.get_status)
        self.register_receive(
            'registration_numbers_for_cars_with_colour',
            self.get_registration_numbers_for_cars_with_colour)
        self.register_receive(
            'slot_numbers_for_cars_with_colour',
            self.get_slot_numbers_for_cars_with_colour)
        self.register_receive(
            'slot_number_for_registration_number',
            self.get_slot_number_for_registration_number)

    def receive(self):
        # Receive the command from queue
        # and execute associated function
        message = None
        while message is None:
            message = (self.non_blocking_get(self.in_queue)
                       or self.non_blocking_get(self.writer_conn))
        command, sender_queue, args = message
        if command == 'exit':
            sys.exit()
        else:
            fn = self.behaviour[command]
            result = fn() if not args else fn(**args)
            if sender_queue:
                self.put_on_sender(result, sender_queue)

    def park(self, car, slot):
        # Update registration_view
        reg_no = car.get_registration_number()
        color = car.get_color()
        self.registration_view[reg_no] = {
                        'slot': slot,
                        'car': car,
                        'cv_idx': len(self.color_view[color])}
        # Update color view
        self.color_view[color].append(reg_no)

    def leave(self, slot, car):
        reg_no = car.get_registration_number()
        color = car.get_color()
        car_meta = self.registration_view.pop(reg_no)
        self.color_view[color].pop(car_meta['cv_idx'])

    def get_status(self):
        cars = [{'slot': c['slot'],
                 'rno': c['car'].get_registration_number(),
                 'color': c['car'].get_color()} for c in 
                sorted([c for c in self.registration_view.values()],
                        key=lambda cdata: cdata['slot'])]
        cars = [{'slot': 'Slot No.',
                 'rno': 'Registration No',
                 'color': 'Colour'}] + cars
        ljust_sn = max([len(str(c['slot'])) for c in cars])
        ljust_rn = max([len(str(c['rno'])) for c in cars])
        ljust_c = max([len(str(c['color'])) for c in cars])
        status = '\n'.join(['{} {} {}'.format(
                        str(c['slot']).ljust(ljust_sn),
                        str(c['rno']).ljust(ljust_rn),
                        str(c['color']).ljust(ljust_c)) 
                            for c in cars])
        return status

    def get_registration_numbers_for_cars_with_colour(self, color):
        return ",".join(self.color_view[color])

    def get_slot_numbers_for_cars_with_colour(self, color):
        return ",".join([str(self.registration_view[rno]['slot'])
                         for rno in self.color_view[color]])

    def get_slot_number_for_registration_number(self, rno):
        return (self.registration_view[rno]['slot']
                if rno in self.registration_view
                else 'Not found')


from collections import defaultdict

from parkinglot.util.actor import Actor

class ReadSideLot(Actor):
    def __init__(self, name, num_slots, in_queue):
        super().__init__(in_queue)
        registration_view = {}
        color_view = defaultdict([])
        self.register_receive('park', self.park)
        self.register_receive('leave', self.leave)
        self.register_receive('status', self.get_status)
        self.register_receive(
            'registration_numbers_for_cars_with_colour',
            self.get_registration_numbers_for_cars_with_colour)
        self.register_receive(
            'get_slot_numbers_for_cars_with_colour',
            self.get_get_slot_numbers_for_cars_with_colour)
        self.register_receive(
            'get_slot_number_for_registration_number',
            self.get_get_slot_number_for_registration_number)

    def park(self, car, slot):
        # Update registration_view
        reg_no = car.get_registration_number()
        color = car.get_color()
        registration_view[reg_no] = {'slot': slot,
                                     'car': car,
                                     'cv_idx': len(color_view[color])}
        # Update color view
        color_view[color].append(car.get_registration_number())

    def leave(self, slot, car):
        reg_no = car.get_registration_number()
        color = car.get_color()
        car_meta = registration_view.pop(reg_no)
        color_view[color].pop(car_meta['cv_idx'])

    def get_status(self, sender_queue):
        cars = [{'slot': c['slot'],
                 'rno': c['car'].get_registration_number(),
                 'color': c['car'].get_color()} for c in 
                sorted([c for c in registration_view.values()],
                        key=lambda cdata: cdata['slot'])]
        ljust_sn = max([len(str(c['slot'])) for c in cars])
        ljust_rn = max([len(str(c['rno'])) for c in cars])
        ljust_c = max([len(str(c['color'])) for c in cars])
        cars = [{'slot': 'Slot No.',
                 'rno': 'Registration No',
                 'color': 'Colour'}] + cars
        status = "\n".join(["{} {} {}".format(c['slot'].ljust(ljust_sn),
                                              c['rno'].ljust(ljust_rn),
                                              c['color'].ljust(ljust_c)) 
                            for c in cars])
        return status

    def get_registration_numbers_for_cars_with_colour(self, color):
        return ",".join(color_view[color])

    def get_slot_numbers_for_cars_with_colour(self, color):
        return ",".join([registration_view[rno]['slot']
                         for rno in color_view[color]])

    def get_slot_number_for_registration_number(self, rno):
        return registration_view[rno]['slot']


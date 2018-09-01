class Car:
    def __init__(self, registration_number, color):
        self.registration_number = registration_number
        self.color = color

    def get_color(self):
        return self.color

    def get_registration_number(self):
        return self.registration_number
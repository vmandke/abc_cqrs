class Car:
    def __init__(self, registration_number, color):
        self.registration_number = str(registration_number)
        self.color = str(color)

    def get_color(self):
        return self.color

    def get_registration_number(self):
        return self.registration_number
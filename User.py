class User(object):

    def __init__(self, state ):
        self.identifier = 0
        self.name = ""
        self.surname = ""
        self.number = 0
        self.birth_date = ""
        self.country = ""
        self.city = ""
        self.bonus_points = 0
        self.state = state

    def change_state(self):
        self.state = self.state + 1

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_state(self):
        return self.state
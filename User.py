class User(object):

    def __init__(self, identifier, name, surname, number, birth_date, country, city, bonus_points):
        self.identifier = identifier
        self.name = name
        self.surname = surname
        self.number = number
        self.birth_date = birth_date
        self.country = country
        self.city = city
        self.bonus_points = bonus_points

    def __init__(self, identifier):
        self.identifier = identifier
        self.name = ""
        self.surname = ""
        self.number = ""
        self.birth_date = ""
        self.country = ""
        self.city = ""
        self.bonus_points = 0

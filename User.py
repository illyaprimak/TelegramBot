class User(object):

    def __init__(self, identifier=None, name=None, surname=None, number=None, birth_date=None, country=None, city=None,
                 bonus_points=None, cards=[]):
        self.identifier = identifier
        self.name = name
        self.surname = surname
        self.number = number
        self.birth_date = birth_date
        self.country = country
        self.city = city
        self.bonus_points = bonus_points
        self.cards = cards
        self.currently_used_vehicle = None

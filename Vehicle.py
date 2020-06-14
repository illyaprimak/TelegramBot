class Vehicle(object):

    def __init__(self, identifier=None, taken=None, technical_state=None, last_tech_service=None, charge_level=None,
                 cents_per_minute=None, zone_id=None, latitude=None, longitude=None):
        self.identifier = identifier
        self.taken = taken
        self.technical_state = technical_state
        self.last_tech_service = last_tech_service
        self.charge_level = charge_level
        self.cents_per_minute = cents_per_minute
        self.zone_id = zone_id
        self.latitude = latitude
        self.longitude = longitude

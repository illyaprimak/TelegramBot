import psycopg2

import User
import Employee
import Card
import Vehicle
import Zone


class Controller(object):

    def __init__(self, dbname, user, password, host):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def insert(self, instance):
        if type(instance) == User.User:
            self.cursor.execute("INSERT INTO user_customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                                (instance.identifier, instance.name, instance.surname,
                                 instance.number, instance.birth_date,
                                 instance.country, instance.city, instance.bonus_points))
        elif type(instance) == Employee.Employee:
            self.cursor.execute("INSERT INTO employee VALUES(%s, %s)",
                                (instance.identifier, instance.specialization))
        elif type(instance) == Card.Card:
            self.cursor.execute("INSERT INTO card (name, user_id) VALUES(%s, %s)",
                                (instance.name, instance.owner))
        elif type(instance) == Vehicle.Vehicle:
            self.cursor.execute("INSERT INTO vehicle VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (instance.identifier, instance.taken, instance.technical_state,
                                 instance.last_tech_service, instance.charge_level,
                                 instance.cents_per_minute, instance.zone_id, instance.latitude, instance.longitude))
        elif type(instance) == Zone.Zone:
            self.cursor.execute("INSERT INTO allowed_zone VALUES(%s, %s, %s)",
                                (instance.identifier, instance.area, instance.location))
        self.conn.commit()

    def get_all(self, table_name):
        self.cursor.execute('SELECT * FROM ' + table_name)
        return self.cursor.fetchall()

    def user_exists(self, identifier):
        self.cursor.execute('SELECT * FROM user_customer WHERE user_id = ' + str(identifier))
        return self.cursor.fetchall()

    def employee_exists(self, identifier):
        self.cursor.execute('SELECT * FROM employee WHERE employee_id = ' + str(identifier))
        return self.cursor.fetchall()

    def get_cards(self, user):
        self.cursor.execute('SELECT * FROM card WHERE user_id = ' + str(user.identifier))
        return self.cursor.fetchall()

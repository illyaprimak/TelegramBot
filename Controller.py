from datetime import datetime
from pprint import pprint

import psycopg2

import User
import Employee
import Card
import Vehicle
import Zone
import Serve
import datetime


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
        elif type(instance) == Serve.Serve:
            self.cursor.execute("INSERT INTO employee_serves_vehicle(employee_id,vehicle_id) VALUES(%s, %s)",
                                (instance.employee_id, instance.vehicle_id))
        self.conn.commit()

    def serve_vehicle(self, vehicle_id):
        self.cursor.execute('UPDATE vehicle SET charge_level = 100 WHERE vehicle_id = %s', vehicle_id)
        self.conn.commit()

    def repair_vehicle(self):
        today = '\'' + str(datetime.date.today().year) + '-' + str(datetime.date.today().month) + '-' + str(
            datetime.date.today().day) + '\''
        sql = 'UPDATE vehicle SET last_tech_service = ' + today + ', technical_state=True WHERE vehicle_id IN(SELECT vehicle_id FROM employee_serves_vehicle WHERE serve_id IN(SELECT MAX(serve_id) FROM employee_serves_vehicle))'
        self.cursor.execute(sql)
        self.conn.commit()

    def get_all(self, table_name):
        self.cursor.execute('SELECT * FROM ' + table_name)
        return self.cursor.fetchall()

    def get_all_vehicles_for_user(self):
        self.cursor.execute(
            'SELECT * FROM vehicle WHERE charge_level > 20 AND taken = false AND technical_state = true')
        return self.cursor.fetchall()

    def get_all_vehicles_for_charger(self):
        self.cursor.execute(
            'SELECT * FROM vehicle WHERE charge_level < 20 AND taken = false')
        return self.cursor.fetchall()

    def get_all_vehicles_for_repairer(self):
        self.cursor.execute(
            'SELECT * FROM vehicle WHERE technical_state = false AND taken = false')
        return self.cursor.fetchall()

    def get_vehicle(self, identifier):
        self.cursor.execute('SELECT * FROM vehicle WHERE vehicle_id = %s', identifier)
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

    def get_specialization(self, identifier):
        self.cursor.execute('SELECT specialization FROM employee WHERE employee_id = ' + str(identifier))
        return self.cursor.fetchall()

    def get_statistic(self, identifier):
        self.cursor.execute(
            "CREATE OR REPLACE VIEW a AS SELECT vehicle_id,COUNT(employee_id) AS \"number1\" FROM employee_serves_vehicle WHERE employee_id IN(SELECT employee_id FROM employee WHERE employee_id = %s ) GROUP BY vehicle_id; CREATE OR REPLACE VIEW b AS SELECT vehicle_id,COUNT(*) AS \"number2\" FROM employee_serves_vehicle GROUP BY vehicle_id; SELECT a.vehicle_id, a.number1, b.number2 FROM A INNER JOIN B ON A.vehicle_id = B.vehicle_id; ",
            [identifier])
        return self.cursor.fetchall()

    def get_broken_users(self):
        self.cursor.execute(
            "SELECT user_name,user_id FROM user_customer WHERE user_id IN( SELECT user_id FROM user_uses_vehicle WHERE end_time  IN( SELECT MAX(end_time) AS max_time FROM user_uses_vehicle WHERE vehicle_id IN( SELECT vehicle_id  FROM vehicle WHERE technical_state = False) GROUP BY vehicle_id	 ))")
        return self.cursor.fetchall()

    def get_employee_by_zone_radius(self, radius):
        self.cursor.execute(
            'SELECT * FROM employee AS E WHERE NOT EXISTS ( SELECT * FROM vehicle AS V WHERE zone_id IN(SELECT zone_id FROM allowed_zone WHERE radius < %s) AND NOT EXISTS (SELECT * FROM employee_serves_vehicle AS S WHERE S.employee_id = E.employee_id AND S.vehicle_id = V.vehicle_id))',
            (
                [radius]
            ))
        try:
            return self.cursor.fetchall()
        except:
            return []

    def end_vehicle_rent(self, vehicle, latitude, longitude, zone_id):
        self.cursor.execute(
            'UPDATE vehicle SET latitude = %s, longitude = %s, taken = %s, zone_id = %s WHERE vehicle_id = %s', (
                latitude, longitude, bool(False), zone_id, vehicle.identifier
            ))

    def add_ride(self, user, vehicle):
        self.cursor.execute('INSERT INTO user_uses_vehicle (start_time, user_id, vehicle_id) VALUES(%s, %s, %s)', (
            datetime.datetime.now(), user.identifier, vehicle.identifier))
        self.conn.commit()

        self.cursor.execute(
            'UPDATE vehicle SET taken = %s WHERE vehicle_id = %s', (bool(True), vehicle.identifier))
        self.conn.commit()

    def end_ride(self, end_time, user, vehicle, payment):
        self.cursor.execute(
            'UPDATE user_uses_vehicle SET end_time = %s, payment = %s WHERE user_id = %s AND vehicle_id = %s AND end_time IS NULL',
            (end_time, payment, user.identifier, vehicle.identifier))
        self.conn.commit()

    def get_ride(self, user, vehicle):
        self.cursor.execute(
            'SELECT * FROM user_uses_vehicle WHERE end_time IS NULL AND user_id = %s AND vehicle_id = %s', (
                user.identifier, vehicle.identifier
            ))
        return self.cursor.fetchall()

    def update_bonuses(self, user):
        self.cursor.execute('UPDATE user_customer SET bonus_points = %s WHERE user_id = %s', (
            user.bonus_points, user.identifier
        ))
        self.conn.commit()

    def get_payments_sum(self, user):
        self.cursor.execute('SELECT user_id, SUM(payment) FROM user_uses_vehicle WHERE user_id = %s GROUP BY user_id', (
            [user.identifier]
        ))
        return self.cursor.fetchall()

    def get_users_rides(self, user):
        self.cursor.execute(
            'SELECT start_time, end_time, payment FROM user_uses_vehicle WHERE payment IS NOT NULL AND user_id = %s', (
                [user.identifier]
            ))
        return self.cursor.fetchall()

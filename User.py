import psycopg2


class User(object):

    def __init__(self, identifier, name, surname, number, birth_date, country, city, bonus_points):
        self.__identifier = identifier
        self.__name = name
        self.__surname = surname
        self.__number = number
        self.__birth_date = birth_date
        self.__country = country
        self.__city = city
        self.__bonus_points = bonus_points

    def add(self):
        conn = psycopg2.connect(dbname='dcur3f5qg9nbp9', user='tbhawhpdqppahx',
                                password='2a58a610fa0064b79d45735606512a9994a9c43a4b2ba30dc3467ae3c375af26',
                                host='ec2-18-232-143-90.compute-1.amazonaws.com')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                       (self.__identifier, self.__name, self.__surname,
                        self.__number, self.__birth_date, self.__birth_date,
                        self.__country, self.__city, self.__bonus_points))
        conn.commit()
        cursor.close()
        conn.close()

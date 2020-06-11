import psycopg2

class User(object):

    def __init__(self, name, surname, userid):
        """Constructor"""
        self.name = name
        self.surname = surname
        self.userid = userid

    def add(self):
        conn = psycopg2.connect(dbname='dcur3f5qg9nbp9', user='tbhawhpdqppahx',
                                password='2a58a610fa0064b79d45735606512a9994a9c43a4b2ba30dc3467ae3c375af26',
                                host='ec2-18-232-143-90.compute-1.amazonaws.com')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users  VALUES(%s, %s, %s)", (self.userid,self.name, self.surname ))
        conn.commit()
        cursor.close()
        conn.close()
        return "Braking"

    def check(self):

        return "I'm driving!"
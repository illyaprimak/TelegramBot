import psycopg2


class User(object):

    def __init__(self, name, surname, userid):
        """Constructor"""
        self.name = name
        self.surname = surname
        self.userid = userid


    def add(self):
        conn = psycopg2.connect(dbname='d6ib69jeupvh36', user='szvriplnadxleq',
                                password='3f6a5c41af6e1ea4a4cc136566588d23fc243823e23a4c2498de18c01865ac3a',
                                host='ec2-34-197-188-147.compute-1.amazonaws.com')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users  VALUES(%s, %s, %s)", (self.userid, self.name, self.surname))
        conn.commit()
        cursor.close()
        conn.close()
        return "Braking"

    def check(self):
        return "I'm driving!"

from datetime import datetime as date
from mysql.connector import connect, Error
connection = connect(
                host="localhost",
                user="userpy",
                password="123",
                database="python")

def insert(name: str, birthday: date, password: str):
    try:
        with connection:
            with connection.cursor() as cursor:
                add = "INSERT INTO py (name, birthday, password) VALUES (%s, %s, %s)"
                data = (name, birthday, password)
                cursor.execute(add, data)
            connection.commit()
    except Error as e:
        return {"message": e}
    else:
        return cursor.rowcount



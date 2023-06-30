from datetime import datetime
from typing import Any
import ast
from flask import session, redirect, url_for
from mysql.connector import connect, Error
from flask_login import UserMixin


def error_handling(error: Error) -> redirect:
    """Called when exceptions occur, redirects to error page"""
    print(error)
    session.pop("error")
    session["error"] = str(error)
    return redirect(url_for('err.error'))


def check_connection(func):
    """Wrapper for DB methods. Before every commit checks if there is still connection, if not it will try to
    reconnect two times. if connection is not successful and during commit error occurs. in both cases returns
    redirect to error page """

    def wrapper(*args, **kwargs):
        if not args[0].connection.is_connected():
            try:
                args[0].connection.reconnect(2, 1)
            except Error as e:
                return error_handling(e)
        try:
            result = func(*args, **kwargs)
        except Error as e:
            return error_handling(e)
        return result

    return wrapper


class User(UserMixin):

    def __init__(self, key: int, email: str, name: str, password: str, filledInfo=False, birthday=None, gender=None,
                 interested=None, agelower=None, ageupper=None, location=None, images=None, range=None):
        self.name = name
        self.email = email
        self.password = password
        self.key = key
        self.birthday = birthday
        self.filledinfo = filledInfo
        self.gender = gender
        self.interested = None if interested is None else ast.literal_eval(interested)
        self.agelower = agelower
        self.ageupper = ageupper
        self.location = location
        self.range = range
        self.images = images

    def get_id(self) -> int:
        return self.key

    def __repr__(self) -> str:
        return "User named: " + self.name + ", with key: " + str(self.key)

    def get_basic_info(self) -> list[any]:
        """Returns list with user's basic info (key, email, name, encrypted password) wrapped in list"""
        return [self.key, self.email, self.name, self.password, self.filledinfo]

    def get_advanced_info(self) -> list[any]:
        """Returns list with user's advanced info (birthday, gender, lower age limit, upper age limit, image url)
        wrapped in list """
        return [self.birthday, self.gender, self.agelower, self.ageupper, self.range, self.images, self.interested]

    def get_image(self) -> str:
        """Returns url of image"""
        return self.images

    def get_card_info(self):
        """Returns dictionary with user's card info (name, birthday, gender, image)"""
        return {"name": self.name, "birthday": self.birthday, "gender": self.gender, "image": self.images}

    def get_message_info(self) -> dict[str: (str, int, str)]:
        """Returns dictionary with user's name, key, image url"""
        return {"name": self.name, "key": self.key, "images": self.images}

    def get_profile_info(self) -> dict[str: (str, datetime, str, str)]:
        """Returns dictionary with user's name, birthday, gender, image url"""
        return {"name": self.name, "birthday": self.birthday, "gender": self.gender, "img": self.images}


class Message:
    """Implementation for individuals messages send between matched users"""

    def __init__(self, id_message: int, from_user: int, to_user: int, time_stamp: datetime, body_message):
        self.id = id_message
        self.from_user = from_user
        self.to_user = to_user
        self.time_stamp = time_stamp
        self.message = body_message

    def data(self) -> dict[str: (str, datetime)]:
        """Returns dictionary with message's properties (from user, to user, body, timestamp)"""
        return {"from_user": self.from_user, "to_user": self.to_user, "time": self.time_stamp.isoformat(),
                "body": self.message}


class DB(UserMixin):
    SELECT_USER = "SELECT `key`, email, `name`, `password`, filledInfo, birthday, gender, interested, agelower, " \
                  "ageupper, ST_AsText(location), images, `range` FROM people WHERE"
    SELECT_CHAT = "SELECT * FROM chat WHERE"
    UPDATE_USER = "UPDATE people SET"
    MATCHED = "matched"
    ACCEPTED = "accepted"
    DECLINED = "declined"

    def __init__(self, host, user, password, database):
        try:
            self.connection = connect(
                host=host,
                user=user,
                password=password,
                database=database)
            self.connection.cursor(buffered=True)
        except Error as e:
            print(e)

    @check_connection
    def insert_user(self, email: str, name: str, password: str) -> int:
        """Inserts new User to the DB with basic info. Returns number of effected rows"""
        add = "INSERT INTO people (email, name, password, interested) VALUES (%s, %s, %s, JSON_ARRAY())"
        data = (email, name, password)
        return self._execute_commit(add, data)

    @check_connection
    def profile_info(self, data: list, key: int) -> int:
        """Update secondary info about user to the DB. Returns number of effected rows"""
        interest = data.pop(-1)
        format_strings = ','.join(['%s'] * len(interest))
        update = f"{DB.UPDATE_USER} birthday = %s, gender = %s, agelower = %s, ageupper = %s, `range` = %s, images = " \
                 f"%s, interested = JSON_ARRAY({format_strings}), filledInfo = %s WHERE `key` = %s; "
        data.extend([*interest, True, key])
        return self._execute_commit(update, (*data,))

    @check_connection
    def update_location(self, long, lat, key) -> int:
        """Update user's location to the DB. Returns number of effected rows"""
        update = f"{DB.UPDATE_USER} location = POINT(%s, %s) WHERE `key` = %s"
        return self._execute_commit(update, (long, lat, key))

    @check_connection
    def insert_message(self, from_user: int, to_user: int, time: datetime, message: str) -> int:
        """Inserts new Message to the DB. Returns number of effected rows"""
        add = "INSERT INTO chat (from_user, to_user, time, message) VALUES (%s, %s, %s, %s)"
        return self._execute_commit(add, (from_user, to_user, time, message))

    @check_connection
    def get_chat_history(self, current_user: int, other_user: int) -> list[dict[str: (str, datetime)]]:
        """Returns history between two user"""
        select = f"{DB.SELECT_CHAT} from_user IN (%s, %s) AND to_user in (%s, %s) ORDER BY time ASC"
        users = (current_user, other_user, current_user, other_user)
        _, data = self._execute_fetchall(select, users)
        return [Message(*msg).data() for msg in data]

    @check_connection
    def get_last_messages(self, key: int) -> list[dict[str, str | int | Any]] or None:
        """Returns newest send messages between specific user and his matched users"""
        matched_keys = self._select_lists(key, DB.MATCHED)
        if not matched_keys:
            return None
        select = f"{DB.SELECT_CHAT} from_user IN (%s, %s) AND to_user in (%s, %s) ORDER BY time DESC Limit 1"
        values = [(key, other_user, key, other_user) for other_user in matched_keys]
        return_data = list()
        for row in values:
            how_much, data = self._execute_fetchall(select, row)
            if how_much:
                return_data.append(Message(*data[0]).data())
        return return_data

    @check_connection
    def get_matched(self, key: int) -> list[dict[str, str | int | Any]] or None:
        """Returns matched users"""
        matched_keys = self._select_lists(key, DB.MATCHED)
        if not matched_keys:
            return None
        format_strings = ','.join(['%s'] * len(matched_keys))
        select = f"{DB.SELECT_USER} `key` IN ({format_strings});"
        data = self._execute_fetchall(select, (*matched_keys,))[1]
        return [User(*user).get_message_info() for user in data]

    @check_connection
    def get_by_location(self, longitude: float, latitude: float, range: int, key: int, interested: list[str],
                        gender: str,
                        lowerAgeLimit: int, upperAgeLimit: int, birthday: str) -> list[dict]:
        """Returns Users available in specified range around user, age and gender interest and not already accepted,
        declined, matched """
        keys_not_to_show = list()
        for table in (DB.ACCEPTED, DB.DECLINED, DB.MATCHED):
            keys_not_to_show += self._select_lists(key, table)
        keys_not_to_show.append(key)
        string_in_recognized_list = ','.join(['%s'] * len(keys_not_to_show))
        strings_interested_list = ','.join(['%s'] * len(interested))
        select = f"{DB.SELECT_USER} (ST_Distance_Sphere(`location`, point(%s, %s)) *.001) <= %s AND filledInfo AND " \
                 f"gender IN ({strings_interested_list} ) AND NOT `key` IN ({string_in_recognized_list}) AND (" \
                 f"TIMESTAMPDIFF(YEAR, birthday, CURDATE()) BETWEEN %s AND %s) AND (TIMESTAMPDIFF(YEAR, STR_TO_DATE(" \
                 f"%s, '%a, %d %b %Y'), CURDATE()) BETWEEN agelower AND ageupper) AND JSON_SEARCH(interested, 'one', " \
                 f"%s); "
        variables = (longitude, latitude, range, *interested, *keys_not_to_show, lowerAgeLimit,
                     upperAgeLimit, birthday, gender)
        data = self._execute_fetchall(select, variables)[1]
        return [User(*user).__dict__ for user in data]

    @check_connection
    def check_email(self, email: str) -> int:
        """Returns number of rows corresponding to the selected email."""
        select = f"{DB.SELECT_USER} email = %s"
        return self._execute_fetchall(select, (email,))[0]

    @check_connection
    def get_by_email(self, email: str) -> User or None:
        """Returns class User corresponding to the email or None if there was no data found in the DB."""
        select = f"{DB.SELECT_USER} email = %s"
        return self._choose_get_by(select, (email,))

    @check_connection
    def get_by_id(self, key: int) -> User or None:
        """Returns class User corresponding to the id or None if there was no data found in the DB."""
        select = f"{DB.SELECT_USER} `key` = %s"
        return self._choose_get_by(select, (key,))

    @check_connection
    def remove_from_accepted(self, user_key: int, removing_key: int) -> int:
        """Return int of affected rows. Remove user key from accepted column in removing key row."""
        delete = f"DELETE FROM {DB.ACCEPTED} WHERE `key1` = %s AND key2 = %s;"
        return self._execute_commit(delete, (user_key, removing_key))

    @check_connection
    def check_in_accepted(self, user_key: int, checking_key: int) -> int:
        """Checks if user key is in accepted column in checking key row. Should return 1 if key is found, otherwise 0"""
        select = f"SELECT * FROM {DB.ACCEPTED} WHERE `key1` = %s AND key2 = %s"
        return self._execute_fetchall(select, (user_key, checking_key))[0]

    @check_connection
    def add_to_declined(self, user_key: int, declined_key: int) -> int:
        """Adds declined key to the declined column at user key row. Return 1 if addition was successful"""
        return self._add_to(DB.DECLINED, (user_key, declined_key))

    @check_connection
    def add_to_accepted(self, user_key: int, accepted_key: int) -> int:
        """Adds accepted key to the accepted column at user key row. Return 1 if addition was successful"""
        return self._add_to(DB.ACCEPTED, (user_key, accepted_key))

    @check_connection
    def add_to_matched(self, user_key: int, matched_key: int) -> int:
        """Adds matched key to the matched column at user key row. Return 1 if addition was successful"""
        return self._add_to(DB.MATCHED, (user_key, matched_key))

    def _select_lists(self, key: int, table: str) -> list[int]:
        """Return tuple of numbers from table that are in same row with key """
        select = f"SELECT key2 FROM {table} WHERE `key1` = %s;"
        data = self._execute_fetchall(select, (key,))[1]
        return [x[0] for x in data]

    def _add_to(self, table: str, values: tuple) -> int:
        """Add to the column specified number in specified row. Return int of affected rows"""
        update = f"INSERT INTO {table} (`key1`, key2) VALUES (%s, %s);"
        return self._execute_commit(update, values)

    def _choose_get_by(self, select: str, values: tuple) -> User or None or Error:
        """Returns class User, None or Error depending on returned value from DB corresponding to selected command."""
        rows, user = self._execute_fetchall(select, values)
        if rows == 1:
            data = user[0]
            return User(*data)
        elif rows == 0:
            return None
        else:
            raise Error("Wrong number of users: " + str(rows))

    def _execute_fetchall(self, select: str, values: tuple) -> tuple[int, list[any]]:
        """Insert command from select variable. Returns tuple with number of affected rows and datas"""
        with self.connection.cursor() as cursor:
            cursor.execute(select, values)
            data = cursor.fetchall()
            self.connection.commit()
        return cursor.rowcount, data

    def _execute_commit(self, select: str, values: tuple) -> int:
        """Insert command from select variable. Returns number of affected rows"""
        with self.connection.cursor() as cursor:
            cursor.execute(select, values)
            self.connection.commit()
        return cursor.rowcount


db = DB("localhost", "userpy", "123", "python")

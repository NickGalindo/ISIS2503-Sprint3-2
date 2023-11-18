from typing import List
from colorama import Fore
from mysql.connector.pooling import MySQLConnectionPool

from authentication.user import User

async def registerUser(usr: User, password: str, pool: MySQLConnectionPool):
    __db = pool.get_connection()
    __cursor = __db.cursor()

    try:
        __cursor.execute("INSERT INTO auth.users (username, nombre, cedula, ubicacion, password) VALUES (%s, %s, %s, %s, %s);", (usr.username, usr.nombre, usr.cedula, usr.ubicacion, password))
    except Exception as e:
        print(Fore.RED + "ERROR: MySql command failed")
        print(e)

        __cursor.close()
        __db.close()

        raise e

    __db.commit()

    __cursor.close()
    __db.close()

    return True

async def getUserSensitive(username: str, pool: MySQLConnectionPool) -> List:
    __db = pool.get_connection()
    __cursor = __db.cursor()

    try:
        __cursor.execute("SELECT auth.users.username, auth.users.nombre, auth.users.cedula, auth.users.ubicacion, auth.users.password FROM auth.users WHERE auth.users.username = %s;", (username))
    except Exception as e:
        print(Fore.RED + "ERROR: MySql query failed")
        print(e)

        __cursor.close()
        __db.close()

        raise e

    data = __cursor.fetchall()

    __cursor.close()
    __db.close()

    return data

async def getUser(username: str, pool: MySQLConnectionPool) -> List:
    __db = pool.get_connection()
    __cursor = __db.cursor()

    try:
        __cursor.execute("SELECT auth.users.username, auth.users.nombre, auth.users.cedula, auth.users.ubicacion FROM auth.users WHERE auth.users.username = %s;", (username))
    except Exception as e:
        print(Fore.RED + "ERROR: MySql query failed")
        print(e)

        __cursor.close()
        __db.close()

        raise e

    data = __cursor.fetchall()

    __cursor.close()
    __db.close()

    return data

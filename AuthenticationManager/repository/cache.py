from datetime import timedelta
import redis
from colorama import Fore

def checkJwtBlacklist(token: str, redis_connection_pool: redis.ConnectionPool):
    __redis = redis.Redis(connection_pool=redis_connection_pool)

    try:
        if __redis.get(token) is not None:
            return True
    except Exception as e:
        print(Fore.RED + "ERROR: Failed to check jwt blacklist falling back to default blacklisted")
        print(e)
        return True

    return False

def addJwtBlacklist(token: str, exp: timedelta, redis_connection_pool: redis.ConnectionPool):
    __redis = redis.Redis(connection_pool=redis_connection_pool)

    try:
        __redis.setex(token, exp, 1)
    except Exception as e:
        print(Fore.RED + "ERROR: Couldn't blacklist jwt token")
        print(e)
        return False

    return True

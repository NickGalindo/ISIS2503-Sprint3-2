from manager.load_config import CONFIG

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from authentication import router as authentication_router

from mysql.connector.pooling import MySQLConnectionPool
import redis

import colorama
from colorama import Fore


colorama.init(autoreset=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.sqlConnectionPool = MySQLConnectionPool(
            host=CONFIG["MYSQL_HOST"],
            user=CONFIG["MYSQL_USER"],
            password=CONFIG["MYSQL_PASSWORD"],
            pool_name="auth_pool",
            pool_size=8
        )
    except Exception as e:
        print(Fore.RED + "ERROR: Couldn't establish connection with MySql database")
        raise e

    try:
        app.state.redisConnectionPool = redis.ConnectionPool(
            host=CONFIG["REDIS_HOST"],
            port=CONFIG["REDIS_PORT"],
            decode_responses=True
        )
    except Exception as e:
        print(Fore.RED + "ERROR: connection to redis cache failed")
        raise e

    yield

    app.state.sqlConnectionPool._remove_connections()
    app.state.redisConnectionPool.disconnect()


app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None, lifespan=lifespan)

origins= ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authentication_router, prefix="/auth")

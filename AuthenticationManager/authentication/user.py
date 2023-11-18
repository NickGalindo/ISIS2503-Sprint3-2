from typing import Annotated, Dict

from colorama import Fore

from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from passlib.context import CryptContext

from authentication.jwt import JwtToken, createAccessToken, decodeAccessToken, createRefreshToken

from mysql.connector.pooling import MySQLConnectionPool
from repository import dbconnect

from authentication.models import User

# Hashing
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def __verifyPassword(password: str, db_password: str):
    return PWD_CONTEXT.verify(password, db_password)

def __hashPassword(password: str):
    return PWD_CONTEXT.hash(password)


# database interaction
async def __authenticate(pool: MySQLConnectionPool, username: str, password: str) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        db_resp = await dbconnect.getUserSensitive(username, pool)
    except Exception as e:
        print(Fore.RED + "ERROR: Couldn't find user in db")

        raise credentials_exception

    db_password = db_resp[0][4]

    if not __verifyPassword(password, db_password):
        raise credentials_exception

    usr = User(
        username=db_resp[0][0], 
        nombre=db_resp[0][1],
        cedula=db_resp[0][2],
        ubicacion=db_resp[0][3]
    )

    return usr

async def __register(pool: MySQLConnectionPool, usr: User, password: str) -> bool:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        db_resp = await dbconnect.registerUser(usr, __hashPassword(password), pool)
    except Exception as e:
        print(Fore.RED + "ERROR: Couldn't register user")
        raise credentials_exception

    return db_resp


# user functions
async def getCurrentUser(decoded_token: Annotated[Dict, Depends(decodeAccessToken)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if not decoded_token.get("sub"):
        raise credentials_exception

    try:
        user = User(
            username=decoded_token["username"],
            nombre=decoded_token["nombre"],
            cedula=decoded_token["cedula"],
            ubicacion=decoded_token["ubicacion"]
        )
    except KeyError:
        raise credentials_exception

    return user

async def loginUser(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Dict[str, JwtToken | User]:
    user = await __authenticate(request.app.state.sqlConnectionPool, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Couldn't validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = await createAccessToken(
        data={
            "username": user.username,
            "nombre": user.nombre,
            "cedula": user.cedula,
            "ubicacion": user.ubicacion,
            "sub": user.cedula
        }
    )

    refresh_token = await createRefreshToken(
        data={
            "username": user.username,
            "nombre": user.nombre,
            "cedula": user.cedula,
            "ubicacion": user.ubicacion,
        }
    )

    return {"access_token": JwtToken(token=access_token, token_type="bearer"), "refresh_token": JwtToken(token=refresh_token, token_type="bearer"), "User": user}

async def registerUser(request: Request, username: Annotated[str, Form()], nombre: Annotated[str, Form()], cedula: Annotated[str, Form()], ubicacion: Annotated[str, Form()], password: Annotated[str, Form()]):
    usr = User(
        username=username,
        nombre=nombre,
        cedula=cedula,
        ubicacion=ubicacion
    )

    return await __register(request.app.state.sqlConnectionPool, usr, password)

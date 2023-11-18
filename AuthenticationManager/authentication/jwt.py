import redis
from manager.load_config import CONFIG
from typing import Dict, Any

from datetime import datetime, timedelta

from typing import Annotated
from fastapi import Depends, Form, HTTPException, status
from pydantic import BaseModel

from fastapi.security import OAuth2PasswordBearer

import jwt

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets
import base64

from repository import cache

# Class for a JWT token
class JwtToken(BaseModel):
    token: str
    token_type:str

# Extract username and password from Form()
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="auth/login")
# Extract refresh token from Form()
async def extractRefreshToken(refresh_token: Annotated[str, Form()]) -> str:
    return refresh_token

# Create Tokens
async def encryptPayload(data: Dict) -> Dict:
    for key in data:
        if key == "exp":
            continue
        
        noonce = secrets.token_bytes(12)
        val_encrypted = noonce + AESGCM(base64.b64decode(CONFIG["PAYLOAD_KEY"])).encrypt(noonce, data[key].encode(), b"")
        data[key] = base64.b64encode(val_encrypted).decode("utf-8")

    return data

async def createAccessToken(data: Dict, expires_delta: timedelta = timedelta(minutes=CONFIG["ACCESS_TOKEN_EXPIRE_MINUTES"])):
    to_encode = await encryptPayload(data.copy())

    expire: datetime = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, CONFIG["ACCESS_SECRET_KEY"], algorithm=CONFIG["ENCRYPT_ALGORITHM"])

    return encoded_jwt

async def createRefreshToken(data: Dict, expires_delta: timedelta = timedelta(weeks=CONFIG["REFRESH_TOKEN_EXPIRE_WEEKS"])):
    to_encode = await encryptPayload(data.copy())

    expire: datetime = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, CONFIG["REFRESH_SECRET_KEY"], algorithm=CONFIG["ENCRYPT_ALGORITHM"])

    return encoded_jwt

# Decode Tokens
async def decryptPayload(data: Dict) -> Dict:
    for key in data:
        if key == "exp":
            continue
        val_encoded = base64.b64decode(data[key].encode("UTF-8"))
        data[key] = AESGCM(base64.b64decode(CONFIG["PAYLOAD_KEY"])).decrypt(data[:12], data[12:], b"").decode()

    return data

async def decodeAccessToken(token: Annotated[str, Depends(OAUTH2_SCHEME)]) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        decoded_token = jwt.decode(token, CONFIG["ACCESS_SECRET_KEY"], algorithms=[CONFIG["ENCRYPT_ALGORITHM"]])
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    return await decryptPayload(decoded_token)

async def decodeRefreshToken(refresh_token: str) -> Dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        decoded_token = jwt.decode(refresh_token, CONFIG["REFRESH_SECRET_KEY"], algorithms=[CONFIG["ENCRYPT_ALGORITHM"]])
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    return await decryptPayload(decoded_token)

# Refresh Tokens
async def refreshAccessToken(redis_connection_pool: redis.ConnectionPool, token: Annotated[str, Depends(extractRefreshToken)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if cache.checkJwtBlacklist(token, redis_connection_pool):
        raise credentials_exception

    data: Dict = await decodeRefreshToken(token)

    calc_time_exp = data["exp"]

    if not cache.addJwtBlacklist(token, timedelta(seconds=calc_time_exp), redis_connection_pool):
        raise credentials_exception

    refresh_token = await createRefreshToken(data=data)
    data["sub"] = data["cedula"]
    access_token = await createAccessToken(data=data)

    return {"access_token": JwtToken(token=access_token, token_type="bearer"), "refresh_token": JwtToken(token=refresh_token, token_type="bearer")}

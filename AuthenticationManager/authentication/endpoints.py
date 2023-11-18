from typing import Annotated, Dict
from fastapi import APIRouter, Depends

from authentication.user import loginUser, registerUser, getCurrentUser, User
from authentication.jwt import JwtToken, refreshAccessToken

router = APIRouter()

@router.post("/login")
async def login(tokens: Annotated[Dict[str, JwtToken | User], Depends(loginUser)]) -> Dict[str, JwtToken | User]:
    return tokens

@router.post("/register")
async def register(success: Annotated[bool, Depends(registerUser)]):
    return {"Status": "Registration complete"}

@router.get("/user")
async def getUser(user: Annotated[User, Depends(getCurrentUser)]) -> User:
    return user

@router.post("/refreshToken")
async def refreshToken(tokens: Annotated[Dict[str, JwtToken], Depends(refreshAccessToken)]) -> Dict[str, JwtToken]:
    return tokens

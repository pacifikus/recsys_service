import os
from datetime import datetime, timedelta
from typing import Union

from dotenv import find_dotenv, load_dotenv
from jose import jwt
from passlib.context import CryptContext

from service.models import User

load_dotenv(find_dotenv())

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
BOT_NAME = os.getenv("BOT_USERNAME")
BOT_PASSWORD = os.getenv("PASSWORD")
ACCESS_TOKEN_EXPIRE_MINUTES = 30240

users_db = {
    BOT_NAME: {
        "username": BOT_NAME,
        "hashed_password": BOT_PASSWORD,
    }
}
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: dict, username: str) -> Union[User, None]:
    if username in db:
        user_dict = db[username]
        return User(**user_dict)
    return None


def authenticate_user(
    db: dict,
    username: str,
    password: str,
) -> Union[User]:
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    data: dict,
    expires_delta: Union[timedelta, None] = None,
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

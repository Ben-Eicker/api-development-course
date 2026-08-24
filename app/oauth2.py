from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from . import config, database, models, schemas

SECRET_KEY = config.settings.secret_key
ALGORITHM = config.settings.algorithm

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

DbSession = Annotated[Session, Depends(database.get_db)]


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return password_hash.hash(password)


def get_user(username: str, db: DbSession):
    """Look up a user by email.

    :param username: The user's email address, despite the parameter name
    :param db: Database session
    :return: The matching user, or None if no user has that email
    """
    user = db.query(models.User).filter(models.User.email == username).first()
    return user


def authenticate_user(username: str, password: str, db: DbSession):
    """Verify a user's credentials.

    :param username: The user's email address
    :param password: The plaintext password to check
    :param db: Database session
    :return: The user if the credentials are valid, otherwise False
    """
    user = get_user(username, db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Encode a JWT access token.

    :param data: Claims to embed in the token, e.g. {"sub": user.email}
    :param expires_delta: Time until expiry; defaults to 15 minutes if not given
    :return: The encoded JWT
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession):
    """Resolve the current user from a bearer token, for use as a FastAPI dependency.

    :param token: JWT bearer token from the Authorization header
    :param db: Database session
    :raises HTTPException: 401 if the token is missing, invalid, expired, or names a
        user that no longer exists
    :return: The authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(token_data.username, db)  # pyright: ignore
    if user is None:
        raise credentials_exception
    return user

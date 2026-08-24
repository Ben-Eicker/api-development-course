from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import config, database, oauth2, schemas

router = APIRouter(prefix="/login", tags=["Authentication"])

DbSession = Annotated[Session, Depends(database.get_db)]
UserCredentials = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/", response_model=schemas.Token)
def login(user_credentials: UserCredentials, db: DbSession):
    """Authenticate a user by credentials and issue an access token.

    :param user_credentials:
        OAuth2 form containing username and password
    :param db:
        Database session
    :raises HTTPException:
        When the credentials are invalid (401)
    :return:
        Access token if the user was successfully authenticated
    """
    user = oauth2.authenticate_user(user_credentials.username, user_credentials.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
        )
    access_token_expires = timedelta(minutes=config.settings.access_token_expire_minutes)
    access_token = oauth2.create_access_token(
        {"sub": user.email}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")

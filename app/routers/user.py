from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database, models, oauth2, schemas

router = APIRouter(prefix="/users", tags=["Users"])

DbSession = Annotated[Session, Depends(database.get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: DbSession):
    """Create a new user."""
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"user with email: {user.email} already exists",
        )
    user.password = oauth2.get_password_hash(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: DbSession):
    """Retrieve a single user by id."""
    user = db.query(models.User).filter(models.User.user_id == id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id: {id} does not exist",
        )
    return user

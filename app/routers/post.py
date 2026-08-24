from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import database, models, oauth2, schemas

router = APIRouter(prefix="/posts", tags=["Posts"])

DbSession = Annotated[Session, Depends(database.get_db)]
User = Annotated[schemas.UserResponse, Depends(oauth2.get_current_user)]


@router.get("/", response_model=list[schemas.PostResponse])
def get_posts(
    db: DbSession,
    user: User,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    search: str = "",
):
    """Retrieve all posts with their vote counts."""
    results = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.post_id, isouter=True)
        .filter(models.Post.title.contains(search))
        .group_by(models.Post.post_id)
        .order_by(models.Post.post_id)
        .limit(limit)
        .offset(skip)
        .all()
    )
    return [
        schemas.PostResponse.model_validate(post).model_copy(update={"votes": votes})
        for post, votes in results
    ]


@router.get("/{id}", response_model=schemas.PostResponse)
def get_post(id: int, db: DbSession, user: User):
    """Retrieve a single post by id, with its vote count."""
    result = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.post_id, isouter=True)
        .filter(models.Post.post_id == id)
        .group_by(models.Post.post_id)
        .first()
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )
    post, votes = result
    return schemas.PostResponse.model_validate(post).model_copy(update={"votes": votes})


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: DbSession, user: User):
    """Create a new post."""
    new_post = models.Post(**post.model_dump(), user_id=user.user_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: DbSession, user: User):
    """Delete a post by id."""
    post_query = db.query(models.Post).filter(models.Post.post_id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )
    if post.user_id != user.user_id:  # pyright: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized to perform requested action",
        )
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostCreate, db: DbSession, user: User):
    """Update a post by id."""
    post = db.query(models.Post).filter(models.Post.post_id == id).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )
    if post.user_id != user.user_id:  # pyright: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized to perform requested action",
        )
    for field, value in updated_post.model_dump().items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post

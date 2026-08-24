from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database, models, oauth2, schemas

router = APIRouter(prefix="/vote", tags=["Vote"])

DbSession = Annotated[Session, Depends(database.get_db)]
User = Annotated[schemas.UserResponse, Depends(oauth2.get_current_user)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.VoteBase, db: DbSession, user: User):
    """Cast or retract the current user's vote on a post.

    :param vote: Post id and direction (1 to upvote, 0 to remove the
        vote)
    :param db: Database session
    :raises HTTPException: If the post does not exist, the vote already
        exists (409), or the vote to remove does not exist (404)
    :return: Confirmation message describing the action taken
    """
    post = db.query(models.Post).filter(models.Post.post_id == vote.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {vote.post_id} does not exist",
        )
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == user.user_id
    )
    found_vote = vote_query.first()
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"user {user.user_id} has already voted on post {vote.post_id}",
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=user.user_id)
        db.add(new_vote)
        db.commit()
        return {"message": "successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"vote by user {user.user_id} on post {vote.post_id} does not exist",
            )
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "successfully removed vote"}

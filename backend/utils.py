from fastapi import HTTPException
from sqlalchemy.orm import Session

from constants import USER_NOT_FOUND
from models import User
from http import HTTPStatus


def get_authenticated_user(db: Session, current_user: dict):
    """
    Fetch authenticated user from the database.

    Raises:
        HTTPException: 404 if user is not found.

    Returns:
        User: Authenticated user object.
    """
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=USER_NOT_FOUND)
    return user

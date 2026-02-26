from fastapi import Request
from sqlalchemy.orm import Session
from auth import decode_token
from models import User


def get_current_user(request: Request, db: Session) -> User | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    email = decode_token(token)
    if not email:
        return None
    user = db.query(User).filter(User.email == email).first()
    return user

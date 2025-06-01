from model.models import Member
from dto.user import UserCreate
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

def create_user(db: Session, user_data: UserCreate) -> Member:
    hashed_pw = bcrypt.hash(user_data.password)
    user = Member(
        email=user_data.email,
        password=hashed_pw,
        username=user_data.username
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> Member:
    user = db.query(Member).filter(Member.email == email).first()
    if not user or not bcrypt.verify(password, user.password):
        return None
    return user
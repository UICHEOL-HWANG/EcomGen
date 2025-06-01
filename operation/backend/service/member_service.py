from sqlalchemy.orm import Session
from model.models import Member
from dto.user import UserUpdate
from fastapi import HTTPException

def update_user_info(db: Session, user_id: int, update_data: UserUpdate):
    user = db.query(Member).filter(Member.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update_data.username:
        user.username = update_data.username
    if update_data.email:
        user.email = update_data.email

    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
    }

def delete_user(db: Session, user_id: int):
    user = db.query(Member).filter(Member.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
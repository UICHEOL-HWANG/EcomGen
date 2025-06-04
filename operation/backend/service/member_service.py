from sqlalchemy.orm import Session
from model.models import Member
from dto.user import UserUpdate
from fastapi import HTTPException
from passlib.hash import bcrypt

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

def change_user_password(db:Session,
                         user_id: int,
                         current_password: str,
                         new_password: str
                         ):
    user = db.query(Member).filter(Member.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt.verify(current_password, user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # new password

    user.password = bcrypt.hash(new_password)
    db.commit()
    db.refresh(user)

    return {
        "message" : "패스워드 변경 완료"
    }
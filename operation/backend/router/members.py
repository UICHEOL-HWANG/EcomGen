from datetime import datetime
from fastapi import Cookie
from utils.pymongo import get_token_collection
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from model.database import get_db
from core.security import get_current_user, validate_csrf
from dto.user import UserUpdate, UserOut
from service.member_service import update_user_info, delete_user

router = APIRouter(prefix="/member", tags=["member"])

@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
def read_my_info(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    validate_csrf(request)
    return current_user

@router.put("/me", response_model=dict, status_code=status.HTTP_200_OK)
def update_my_info(
    request: Request,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    validate_csrf(request)
    updated_user = update_user_info(db, current_user["id"], update_data)
    return {"message": "User updated", "user": updated_user}

@router.delete("/me", response_model=dict, status_code=status.HTTP_200_OK)
def delete_my_account(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    refresh_token: str = Cookie(None)
):
    validate_csrf(request)

    # 블랙리스트 처리
    if refresh_token:
        token_collection = get_token_collection()
        token_collection.insert_one({
            "token": refresh_token,
            "user_id": current_user["id"],
            "blacklisted_at": datetime.utcnow()
        })

    delete_user(db, current_user["id"])
    return {"message": "User deleted"}
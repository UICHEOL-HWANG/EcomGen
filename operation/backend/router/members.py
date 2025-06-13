# pip Modules
from datetime import datetime
from fastapi import HTTPException, UploadFile, File

from fastapi import Cookie
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

# My Modules
from model.database import get_db
from model.models import Member
from core.security import get_current_user, validate_csrf
from utils.pymongo import get_token_collection
from dto.user import UserUpdate, UserOut, PasswordChange
from service.member_service import update_user_info, delete_user, change_user_password
from service.profile_upload_service import handle_profile_picture_upload, delete_profile_picture



router = APIRouter(prefix="/member", tags=["member"])

@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
def read_my_info(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    validate_csrf(request)
    
    # 데이터베이스에서 최신 사용자 정보 가져오기 (profile_pic 포함)
    user = db.query(Member).filter(Member.id == current_user["id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # UserOut 형식으로 반환 (profile_pic 경로 포함)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at,
        "profile_pic": user.profile_pic  # 프로필 사진 경로 포함
    }

@router.put("/update_account", response_model=dict, status_code=status.HTTP_200_OK)
def update_my_info(
    request: Request,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    validate_csrf(request)
    updated_user = update_user_info(db, current_user["id"], update_data)
    return {"message": "User updated", "user": updated_user}

@router.delete("/delete_account", response_model=dict, status_code=status.HTTP_200_OK)
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



@router.put("/change-password")
def change_password(
        request: Request,
        password_data: PasswordChange,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    validate_csrf(request)

    # 추가 검증들 (confirm_password 등)
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(status_code=400, detail="Password confirmation does not match")

    # service 함수 호출
    return change_user_password(
        db,
        current_user["id"],
        password_data.current_password,
        password_data.new_password
    )

# Upload profile picture route
@router.post("/upload-profile", response_model=dict)
def upload_profile_picture(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    validate_csrf(request)
    return handle_profile_picture_upload(current_user["id"], file)


@router.delete("/delete-profile", response_model=dict)
def delete_profile_picture_route(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    validate_csrf(request)
    return delete_profile_picture(current_user["id"])

from fastapi import HTTPException
from fastapi import UploadFile, File
import base64

from model.database import SessionLocal
from model.models import Member
from utils.storage import CustomUpload

def handle_profile_picture_upload(user_id: str, file: UploadFile) -> dict:
    db = SessionLocal()
    uploader = CustomUpload()

    try:
        # 파일 읽고 base64 인코딩
        file_bytes = file.file.read()
        base64_data = base64.b64encode(file_bytes).decode("utf-8")

        # S3에 업로드
        upload_result = uploader.upload_profile_picture(base64_data, user_id)

        if not upload_result.get("success"):
            raise HTTPException(status_code=500, detail=upload_result.get("error"))

        # DB에 URL 업데이트
        member = db.query(Member).filter(Member.id == user_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        member.profile_pic = upload_result["file_url"]
        db.commit()

        return {
            "success": True,
            "message": "프로필 사진이 업로드되었습니다.",
            "profile_pic_url": upload_result["file_url"]
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


def delete_profile_picture(user_id: str) -> dict:
    db = SessionLocal()
    uploader = CustomUpload()

    try:
        member = db.query(Member).filter(Member.id == user_id).first()
        if not member:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        if member.profile_pic:
            delete_result = uploader.delete_profile_picture(member.profile_pic)

            if not delete_result.get("success"):
                raise HTTPException(status_code=500, detail=delete_result.get("error"))

        member.profile_pic = None
        db.commit()

        return {
            "success": True,
            "message": "프로필 사진이 삭제되었습니다."
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()
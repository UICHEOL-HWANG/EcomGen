from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func

# https://www.erdcloud.com/d/hoHMuauQx6cmzZgaA ERD 기반 설계 완료

class Member(Base):
    __tablename__ = "members"

    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    profile_pic = Column(String(500), nullable=True)  # 프로필 사진 URL (선택 사항)

    product_descriptions = relationship("ProductDescription", back_populates="user")
    reports = relationship("Report", back_populates="user")
    generated_images = relationship("GeneratedImage", back_populates="user", cascade="all, delete-orphan")

class ProductDescription(Base):
    __tablename__ = "product_descriptions"

    id = Column(BigInteger, primary_key=True, index=True)
    job_id = Column(String(36), index=True, nullable=True)  # 추가: UUID 작업 ID
    user_id = Column(BigInteger, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(255), nullable=False)
    input_prompt = Column(Text, nullable=False)
    generated_description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    category = Column(String(255), nullable=True)
    price = Column(Integer, nullable=True)
    keywords = Column(Text, nullable=True)  # Store JSON-encoded keyword list
    tone = Column(String(100), nullable=True)

    user = relationship("Member", back_populates="product_descriptions")

class GeneratedImage(Base):
    __tablename__ = "generated_images"

    id = Column(BigInteger, primary_key=True, index=True)
    job_id = Column(String(36), index=True, nullable=True)  # 추가: UUID 작업 ID
    user_id = Column(BigInteger, ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)

    # 제품 정보
    product_name_ko = Column(String(200), nullable=False, index=True)  # 사용자 입력 한글 제품명
    product_name_en = Column(String(200), nullable=False, index=True)  # 번역된 영문 제품명 (FLUX용)
    prompt_used = Column(Text, nullable=True)  # 실제 사용된 프롬프트

    # 이미지 파일 정보
    file_url = Column(String(500), nullable=False)  # S3 저장된 이미지 URL

    # 생성 시간
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # 관계 설정
    user = relationship("Member", back_populates="generated_images")

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    
    # 추가: 리포트 저장을 위한 필드들
    title = Column(String(255), nullable=True)  # 리포트 제목
    content = Column(Text, nullable=True)  # 정제된 리포트 내용 (마크다운 처리 완료)
    job_id = Column(String(255), nullable=True)  # AI 생성 작업 ID
    
    input_state = Column(JSON)
    output_state = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = relationship("Member", back_populates="reports")

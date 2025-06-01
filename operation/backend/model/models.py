from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Text, JSON
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
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    product_descriptions = relationship("ProductDescription", back_populates="user")
    reports = relationship("Report", back_populates="user")

class ProductDescription(Base):
    __tablename__ = "product_descriptions"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(255), nullable=False)
    generated_description = Column(Text, nullable=False)

    user = relationship("Member", back_populates="product_descriptions")
    showcase_item = relationship("ShowcaseItem", uselist=False, back_populates="product_description")


class ShowcaseItem(Base):
    __tablename__ = "showcase_items"

    id = Column(BigInteger, primary_key=True, index=True)
    product_description_id = Column(BigInteger, ForeignKey("product_descriptions.id", ondelete="CASCADE"), nullable=False)
    displayed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product_description = relationship("ProductDescription", back_populates="showcase_item")

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    run_id = Column(String, nullable=False)  # UUID이지만 문자열로 처리
    input_state = Column(JSON)
    output_state = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("Member", back_populates="reports")
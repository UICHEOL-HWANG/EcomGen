import os
import time
import requests
from dto.product import ProductDescriptionRequest, ProductDescriptionResponse
from service.product_description_service import generate_description_and_save
from fastapi import APIRouter, Body, Request
from dotenv import load_dotenv

from core.security import get_current_user, validate_csrf
from fastapi import Depends
from model.models import ProductDescription
from model.database import get_db
from sqlalchemy.orm import Session

load_dotenv()

router = APIRouter(prefix="/generated", tags=["generate"])

@router.post("/description", response_model=ProductDescriptionResponse)
def generate_product_description(
    request: ProductDescriptionRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    raw_request: Request = None
) -> ProductDescriptionResponse:

    validate_csrf(raw_request) # CSRF 검증

    return generate_description_and_save(request.product_name, current_user["id"], db)
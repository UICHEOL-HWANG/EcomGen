from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import logging
import json
from model.models import Member

from model.database import get_db
from model.models import ProductDescription, GeneratedImage
from core.security import get_current_user, validate_csrf
from service.product_search_service import ProductSearchService
from dto.product import (
    UserProductResponse,
    UserProductsListResponse,
    ProductDeleteResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["product_search"])

@router.get("/my-products", response_model=UserProductsListResponse)
def get_my_products(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=100, description="한 번에 조회할 상품 수"),
    offset: int = Query(default=0, ge=0, description="건너뛸 상품 수"),
    category: Optional[str] = Query(default=None, description="필터링할 카테고리"),
    sort_by: str = Query(default="latest", regex="^(latest|oldest|name|price_low|price_high)$", description="정렬 기준")
):
    """
    현재 사용자가 생성한 상품 목록을 조회합니다.

    - **limit**: 한 번에 조회할 상품 수 (1-100)
    - **offset**: 건너뛸 상품 수 (페이징용)
    - **category**: 특정 카테고리로 필터링 (선택사항)
    - **sort_by**: 정렬 기준 (latest, oldest, name, price_low, price_high)
    """
    try:
        validate_csrf(request)

        # 서비스를 통해 상품 목록과 총 개수 조회
        products, total = ProductSearchService.get_user_products(
            db=db,
            user_id=current_user["id"],
            limit=limit,
            offset=offset,
            category=category,
            sort_by=sort_by
        )

        # 카테고리 목록도 함께 조회
        categories = ProductSearchService.get_user_product_categories(
            db=db,
            user_id=current_user["id"]
        )

        return UserProductsListResponse(
            products=products,
            total=total,
            categories=categories
        )

    except Exception as e:
        logger.error(f"Error in get_my_products: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="상품 목록을 조회하는 중 오류가 발생했습니다."
        )

@router.get("/my-products/{product_id}", response_model=UserProductResponse)
def get_my_product(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    특정 상품의 상세 정보를 조회합니다.
    """
    try:
        validate_csrf(request)

        product = ProductSearchService.get_user_product_by_id(
            db=db,
            user_id=current_user["id"],
            product_id=product_id
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="상품을 찾을 수 없습니다."
            )

        return product

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_my_product: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="상품 정보를 조회하는 중 오류가 발생했습니다."
        )

@router.delete("/my-products/{product_id}", response_model=ProductDeleteResponse)
def delete_my_product(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    특정 상품을 삭제합니다.

    - 해당 상품과 연관된 이미지도 함께 삭제됩니다.
    - 본인이 생성한 상품만 삭제할 수 있습니다.
    """
    try:
        validate_csrf(request)

        success = ProductSearchService.delete_user_product(
            db=db,
            user_id=current_user["id"],
            product_id=product_id
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail="삭제할 상품을 찾을 수 없습니다."
            )

        return ProductDeleteResponse(
            message="상품이 성공적으로 삭제되었습니다.",
            deleted_product_id=product_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_my_product: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="상품을 삭제하는 중 오류가 발생했습니다."
        )

@router.get("/categories", response_model=List[str])
def get_my_product_categories(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    현재 사용자가 생성한 상품의 카테고리 목록을 조회합니다.
    """
    try:
        validate_csrf(request)

        categories = ProductSearchService.get_user_product_categories(
            db=db,
            user_id=current_user["id"]
        )

        return categories

    except Exception as e:
        logger.error(f"Error in get_my_product_categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="카테고리 목록을 조회하는 중 오류가 발생했습니다."
        )

@router.get("/recommended/categories", response_model=List[str])
def get_recommended_product_categories(
    db: Session = Depends(get_db)
):
    """
    추천 상품에서 사용 가능한 카테고리 목록을 조회합니다.
    (이미지가 있는 상품들의 카테고리만 포함)
    """
    try:
        categories = ProductSearchService.get_recommended_product_categories(db=db)
        return categories

    except Exception as e:
        logger.error(f"Error in get_recommended_product_categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="추천 상품 카테고리 목록을 조회하는 중 오류가 발생했습니다."
        )

@router.get("/stats")
def get_my_products_stats(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    현재 사용자의 상품 생성 통계를 조회합니다.

    - 총 상품 수
    - 이미지가 있는 상품 수
    - 카테고리별 분포
    - 완성도 (이미지+텍스트 모두 있는 비율)
    """
    try:
        validate_csrf(request)

        stats = ProductSearchService.get_user_products_stats(
            db=db,
            user_id=current_user["id"]
        )

        return stats

    except Exception as e:
        logger.error(f"Error in get_my_products_stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="통계 정보를 조회하는 중 오류가 발생했습니다."
        )

@router.get("/recommended", response_model=List[UserProductResponse])
def get_recommended_products(
    db: Session = Depends(get_db),
    limit: int = Query(default=6, ge=1, le=100, description="추천 상품 수"),
    category: Optional[str] = Query(default=None, description="카테고리 필터링")
):
    """
    다른 사용자들의 추천 상품을 조회합니다.

    - **limit**: 조회할 추천 상품 수 (1-100)
    - **category**: 특정 카테고리로 필터링 (선택사항)
    - 이미지가 있는 상품만 조회됩니다.
    - 최신 생성 순으로 정렬됩니다.
    - 인증이 필요하지 않은 공개 API입니다.
    """
    try:
        # 🐛 디버깅: 요청 파라미터 로그
        logger.info(f"[DEBUG] 추천 상품 요청 - limit: {limit}, category: {category}")
        
        products = ProductSearchService.get_recommended_products(
            db=db,
            limit=limit,
            category=category
        )
        
        # 🐛 디버깅: 반환 데이터 로그
        logger.info(f"[DEBUG] 추천 상품 결과 - 개수: {len(products)}")
        
        return products

    except Exception as e:
        logger.error(f"Error in get_recommended_products: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=500,
            detail="추천 상품을 조회하는 중 오류가 발생했습니다."
        )

# 검색 기능 (추후 확장 가능)
@router.get("/search", response_model=List[UserProductResponse])
def search_my_products(
    request: Request,
    query: str = Query(..., min_length=1, description="검색어"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=50)
):
    """
    상품명 또는 설명으로 내 상품을 검색합니다.
    """
    try:
        validate_csrf(request)



        results = (
            db.query(ProductDescription, GeneratedImage, Member)
            .outerjoin(
                GeneratedImage,
                ProductDescription.job_id == GeneratedImage.job_id
            )
            .join(
                Member,
                ProductDescription.user_id == Member.id
            )
            .filter(
                ProductDescription.user_id == current_user["id"],
                or_(
                    ProductDescription.product_name.ilike(f"%{query}%"),
                    ProductDescription.generated_description.ilike(f"%{query}%")
                )
            )
            .order_by(ProductDescription.created_at.desc())
            .limit(limit)
            .all()
        )

        # 응답 데이터 구성

        products = []
        for description, image, user in results:
            # keywords JSON 파싱 (안전하게 처리)
            keywords = []
            if description.keywords:
                try:
                    parsed_keywords = json.loads(description.keywords)
                    keywords = parsed_keywords if isinstance(parsed_keywords, list) else []
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"Failed to parse keywords for product {description.id}: {description.keywords}")
                    keywords = []

            product_data = UserProductResponse(
                id=description.id,
                job_id=description.job_id,
                product_name=description.product_name,
                username=user.username,
                profile_pic=user.profile_pic,
                description=description.generated_description,
                category=description.category,
                price=description.price,
                keywords=keywords,
                tone=description.tone,
                image_url=image.file_url if image else None,
                created_at=description.created_at
            )
            products.append(product_data)

        return products

    except Exception as e:
        logger.error(f"Error in search_my_products: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="상품 검색 중 오류가 발생했습니다."
        )

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Tuple
import json
import logging

from model.models import ProductDescription, GeneratedImage, Member
from dto.product import UserProductResponse, UserProductsListResponse

logger = logging.getLogger(__name__)

class ProductSearchService:
    
    @staticmethod
    def get_user_products(
        db: Session, 
        user_id: int, 
        limit: int = 50, 
        offset: int = 0,
        category: Optional[str] = None,
        sort_by: str = "latest"
    ) -> Tuple[List[UserProductResponse], int]:
        """
        사용자가 생성한 상품 목록을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            limit: 조회할 최대 개수
            offset: 오프셋
            category: 필터링할 카테고리 (선택사항)
            sort_by: 정렬 기준 (latest, oldest, name, price_low, price_high)
            
        Returns:
            Tuple[상품 목록, 전체 개수]
        """
        try:
            # 기본 쿼리: ProductDescription과 GeneratedImage를 LEFT JOIN, Member 조인 추가
            query = (
                db.query(ProductDescription, GeneratedImage, Member)
                .outerjoin(
                    GeneratedImage,
                    ProductDescription.job_id == GeneratedImage.job_id
                )
                .join(
                    Member,
                    ProductDescription.user_id == Member.id
                )
                .filter(ProductDescription.user_id == user_id)
            )

            # 카테고리 필터링
            if category:
                query = query.filter(ProductDescription.category == category)

            # 정렬 적용
            if sort_by == "latest":
                query = query.order_by(desc(ProductDescription.created_at))
            elif sort_by == "oldest":
                query = query.order_by(ProductDescription.created_at)
            elif sort_by == "name":
                query = query.order_by(ProductDescription.product_name)
            elif sort_by == "price_low":
                query = query.order_by(ProductDescription.price.nulls_last())
            elif sort_by == "price_high":
                query = query.order_by(desc(ProductDescription.price))
            else:
                # 기본값: 최신순
                query = query.order_by(desc(ProductDescription.created_at))

            # 전체 개수 조회
            total_query = (
                db.query(func.count(ProductDescription.id))
                .filter(ProductDescription.user_id == user_id)
            )
            if category:
                total_query = total_query.filter(ProductDescription.category == category)

            total = total_query.scalar()

            # 페이징 적용하여 결과 조회
            results = query.offset(offset).limit(limit).all()

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
            
            return products, total
            
        except Exception as e:
            logger.error(f"Error fetching user products: {str(e)}")
            raise e
    
    @staticmethod
    def get_user_product_categories(db: Session, user_id: int) -> List[str]:
        """
        사용자가 생성한 상품의 카테고리 목록을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            카테고리 목록
        """
        try:
            categories = (
                db.query(ProductDescription.category)
                .filter(
                    ProductDescription.user_id == user_id,
                    ProductDescription.category.isnot(None),
                    ProductDescription.category != ""
                )
                .distinct()
                .all()
            )
            
            return [cat[0] for cat in categories if cat[0]]
            
        except Exception as e:
            logger.error(f"Error fetching user product categories: {str(e)}")
            raise e
    
    @staticmethod
    def get_user_product_by_id(db: Session, user_id: int, product_id: int) -> Optional[UserProductResponse]:
        """
        특정 상품의 상세 정보를 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            product_id: 상품 ID
            
        Returns:
            상품 정보 (없으면 None)
        """
        try:
            result = (
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
                    ProductDescription.id == product_id,
                    ProductDescription.user_id == user_id
                )
                .first()
            )
            
            if not result:
                return None
            
            description, image, user = result
            
            # keywords JSON 파싱 (안전하게 처리)
            keywords = []
            if description.keywords:
                try:
                    parsed_keywords = json.loads(description.keywords)
                    keywords = parsed_keywords if isinstance(parsed_keywords, list) else []
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"Failed to parse keywords for product {description.id}: {description.keywords}")
                    keywords = []
            
            return UserProductResponse(
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
            
        except Exception as e:
            logger.error(f"Error fetching user product by ID: {str(e)}")
            raise e
    
    @staticmethod
    def delete_user_product(db: Session, user_id: int, product_id: int) -> bool:
        try:
            # 권한 확인을 위해 상품 조회
            product = (
                db.query(ProductDescription)
                .filter(
                    ProductDescription.id == product_id,
                    ProductDescription.user_id == user_id
                )
                .first()
            )
            
            if not product:
                return False
            
            # job_id가 있으면 관련 이미지도 삭제
            if product.job_id:
                db.query(GeneratedImage).filter(
                    GeneratedImage.job_id == product.job_id,
                    GeneratedImage.user_id == user_id
                ).delete(synchronize_session=False)
            
            # 상품 설명 삭제
            db.delete(product)
            db.commit()
            
            logger.info(f"Successfully deleted product {product_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user product: {str(e)}")
            db.rollback()
            raise e
    
    @staticmethod
    def get_user_products_stats(db: Session, user_id: int) -> dict:
        """
        사용자 상품 통계를 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            통계 정보 딕셔너리
        """
        try:
            # 총 상품 수
            total_products = (
                db.query(func.count(ProductDescription.id))
                .filter(ProductDescription.user_id == user_id)
                .scalar()
            )
            
            # 카테고리별 상품 수
            category_stats = (
                db.query(
                    ProductDescription.category,
                    func.count(ProductDescription.id).label('count')
                )
                .filter(
                    ProductDescription.user_id == user_id,
                    ProductDescription.category.isnot(None)
                )
                .group_by(ProductDescription.category)
                .all()
            )
            
            # 이미지가 있는 상품 수
            products_with_images = (
                db.query(func.count(ProductDescription.id))
                .join(GeneratedImage, ProductDescription.job_id == GeneratedImage.job_id)
                .filter(ProductDescription.user_id == user_id)
                .scalar()
            )
            
            return {
                "total_products": total_products,
                "products_with_images": products_with_images,
                "category_breakdown": {cat: count for cat, count in category_stats},
                "completion_rate": (products_with_images / total_products * 100) if total_products > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error fetching user product stats: {str(e)}")
            raise e

    @staticmethod
    def get_recommended_products(
        db: Session,
        limit: int = 6
    ) -> List[UserProductResponse]:
        """
        이미지가 있는 모든 사용자들의 최신 추천 상품을 조회합니다.
        """
        try:
            query = (
                db.query(ProductDescription, GeneratedImage, Member)
                .join(
                    GeneratedImage,
                    ProductDescription.job_id == GeneratedImage.job_id
                )
                .join(
                    Member,
                    ProductDescription.user_id == Member.id
                )
                .filter(
                    GeneratedImage.file_url.isnot(None)
                )
                .order_by(desc(ProductDescription.created_at))
                .limit(limit)
            )

            results = query.all()

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
                    image_url=image.file_url,
                    created_at=description.created_at
                )
                products.append(product_data)

            return products

        except Exception as e:
            logger.error(f"Error fetching recommended products: {str(e)}")
            raise e
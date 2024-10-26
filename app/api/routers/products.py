from typing import List, Optional
from fastapi import APIRouter, Query, Path, Depends
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
import math

from ..exceptions import (
    APIError,
    InternalError,
    NotFoundError,
    InvalidParameterError,
)
from ..response_models import (
    ProductWithReviewsResponse,
    PaginatedProductsResponse,
    PaginatedReviewsResponse,
    PaginatedMetadata,
    ErrorResponse,
)
from database import ProductDB, ReviewDB, get_db


router = APIRouter(prefix="/products")


def validate_sort_parameters(sort_by: Optional[str], valid_fields: List[str]):
    """Validate sort parameters against allowed fields"""
    if sort_by and sort_by not in valid_fields:
        raise InvalidParameterError(
            "sort_by", f"Must be one of: {', '.join(valid_fields)}"
        )


def paginate(query, page: int = 1, limit: int = 10):
    try:
        total = query.count()
        total_pages = math.ceil(total / limit)

        if page > total_pages and total_pages > 0:
            raise InvalidParameterError(
                "page", f"Page {page} exceeds available pages ({total_pages})"
            )

        offset = (page - 1) * limit
        items = query.offset(offset).limit(limit).all()

        metadata = PaginatedMetadata(
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )

        return items, metadata
    except SQLAlchemyError as e:
        raise InternalError(str(e))


@router.get(
    "/",
    response_model=PaginatedProductsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def get_products(
    db: Session = Depends(get_db),
    # Search parameters
    search: Optional[str] = Query(None, description="Search in brand, model, or title"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    model: Optional[str] = Query(None, description="Filter by model"),
    # Filter parameters
    min_price: Optional[float] = Query(None, description="Minimum price", ge=0),
    max_price: Optional[float] = Query(None, description="Maximum price", ge=0),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    # Sort parameters
    sort_by: Optional[str] = Query(
        None,
        description="Sort by field",
    ),
    sort_order: Optional[str] = Query(
        "asc", description="Sort order (asc or desc)", regex="^(asc|desc)$"
    ),
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
):
    try:
        # Validate sort parameters
        valid_sort_fields = ["price", "rating", "review_count"]
        validate_sort_parameters(sort_by, valid_sort_fields)

        # Validate price range
        if min_price is not None and max_price is not None and min_price > max_price:
            raise InvalidParameterError(
                "price_range", "Minimum price cannot be greater than maximum price"
            )

        query = db.query(ProductDB)

        # Apply search filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (ProductDB.brand.ilike(search_term))
                | (ProductDB.model.ilike(search_term))
                | (ProductDB.title.ilike(search_term))
            )

        if brand:
            query = query.filter(ProductDB.brand.ilike(f"%{brand}%"))
        if model:
            query = query.filter(ProductDB.model.ilike(f"%{model}%"))

        # Apply price and rating filters
        if min_price is not None:
            query = query.filter(ProductDB.price >= min_price)
        if max_price is not None:
            query = query.filter(ProductDB.price <= max_price)
        if min_rating is not None:
            query = query.filter(ProductDB.average_rating >= min_rating)

        # Apply sorting
        if sort_by:
            sort_column = getattr(ProductDB, sort_by)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

        # Apply pagination
        items, metadata = paginate(query, page, limit)

        if not items and page > 1:
            raise InvalidParameterError(
                "page", "No results found for the specified page"
            )

        return PaginatedProductsResponse(metadata=metadata, items=items)

    except APIError as e:
        raise
    except Exception as e:
        raise InternalError(f"Unexpected error occurred: {str(e)}")


@router.get(
    "/top",
    response_model=List[ProductWithReviewsResponse],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def get_top_products(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="Number of top products to return"),
    min_reviews: int = Query(5, ge=1, description="Minimum number of reviews required"),
):
    try:
        query = (
            db.query(ProductDB)
            .filter(ProductDB.review_count >= min_reviews)
            .order_by(desc(ProductDB.average_rating), desc(ProductDB.review_count))
            .options(joinedload(ProductDB.reviews))
        )

        top_products = query.limit(limit).all()

        if not top_products:
            raise NotFoundError(
                "Products", f"No products found with minimum {min_reviews} reviews"
            )

        return top_products

    except APIError as e:
        raise
    except Exception as e:
        raise InternalError(f"Unexpected error occurred: {str(e)}")


@router.get(
    "/{product_id}/reviews",
    response_model=PaginatedReviewsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Product Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def get_product_reviews(
    product_id: int = Path(..., description="Product ID"),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Reviews per page"),
    sort_by: Optional[str] = Query("review_date", description="Sort by field"),
    sort_order: Optional[str] = Query(
        "desc", description="Sort order (asc or desc)", regex="^(asc|desc)$"
    ),
):
    try:
        # Validate sort parameters
        valid_sort_fields = ["review_date", "rating"]
        validate_sort_parameters(sort_by, valid_sort_fields)

        # Check if product exists
        product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
        if not product:
            raise NotFoundError("Product", product_id)

        # Query reviews
        query = db.query(ReviewDB).filter(ReviewDB.product_id == product_id)

        # Apply sorting
        sort_column = getattr(ReviewDB, sort_by)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Apply pagination
        items, metadata = paginate(query, page, limit)

        if not items and page > 1:
            raise InvalidParameterError(
                "page", "No reviews found for the specified page"
            )

        return PaginatedReviewsResponse(metadata=metadata, items=items)

    except APIError as e:
        raise
    except Exception as e:
        raise InternalError(f"Unexpected error occurred: {str(e)}")

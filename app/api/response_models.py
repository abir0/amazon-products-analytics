from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# Review Response Models
class ReviewResponse(BaseModel):
    id: int
    reviewer_name: Optional[str]
    rating: Optional[int]
    review_date: Optional[datetime]
    review_text: Optional[str]

    class Config:
        from_attributes = True


# Product Response Models
class ProductBase(BaseModel):
    id: int
    asin: str
    product_url: str
    brand: Optional[str]
    model: Optional[str]
    title: Optional[str]
    price: Optional[float]
    average_rating: Optional[float]
    review_count: Optional[int]
    specifications: Optional[dict[str, str]]
    image_urls: Optional[List[str]]

    class Config:
        from_attributes = True


class ProductResponse(ProductBase):
    pass


class ProductWithReviewsResponse(ProductBase):
    reviews: List[ReviewResponse]


# Pagination Response Models
class PaginatedMetadata(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedProductsResponse(BaseModel):
    metadata: PaginatedMetadata
    items: List[ProductResponse]


class PaginatedReviewsResponse(BaseModel):
    metadata: PaginatedMetadata
    items: List[ReviewResponse]


# Error Response Models
class ErrorResponse(BaseModel):
    detail: str

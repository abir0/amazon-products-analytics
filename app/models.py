from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Review(BaseModel):
    reviewer_name: Optional[str] = Field(alias="name")
    rating: Optional[int]
    review_date: Optional[datetime] = Field(alias="date")
    review_text: Optional[str] = Field(alias="text")


class Product(BaseModel):
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
    top_reviews: Optional[List[Review]]

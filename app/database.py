from datetime import datetime
from typing import Optional

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB

from config import get_config
from api.exceptions import InternalError


config = get_config()

Base = declarative_base()


class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, nullable=False)
    asin = Column(String, unique=True, index=True)
    product_url = Column(String)
    brand = Column(String)
    model = Column(String)
    title = Column(String)
    price = Column(Float)
    average_rating = Column(Float)
    review_count = Column(Integer)
    specifications = Column(JSONB)
    image_urls = Column(JSONB)
    created_at = Column(DateTime, default=datetime.now())

    reviews = relationship("ReviewDB", back_populates="product")


class ReviewDB(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    reviewer_name = Column(String)
    rating = Column(Integer)
    review_date = Column(DateTime)
    review_text = Column(String)
    created_at = Column(DateTime, default=datetime.now())

    product = relationship("ProductDB", back_populates="reviews")


class DatabaseManager:
    def __init__(self, db_url: str):
        self.db_url = db_url or config.DATABASE_URL
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_product(self, product_data: dict) -> ProductDB:
        try:
            Session = self.get_session()
            with Session() as session:
                # Add product data
                db_product = ProductDB(
                    **{
                        k: v
                        for k, v in product_data.items()
                        if k not in ["top_reviews"]
                    }
                )
                session.add(db_product)
                session.flush()

                # Add review data
                for review in product_data.get("top_reviews", []):
                    db_review = ReviewDB(
                        product_id=db_product.id,
                        reviewer_name=review.get("reviewer_name"),
                        rating=review.get("rating"),
                        review_date=review.get("review_date"),
                        review_text=review.get("review_text"),
                    )
                    session.add(db_review)

                session.commit()
        except SQLAlchemyError as e:
            print(f"Error inserting product data: {e}")
        return db_product

    def get_product_by_asin(self, asin: str) -> Optional[ProductDB]:
        try:
            Session = self.get_session()
            with Session(self.engine) as session:
                return session.query(ProductDB).filter(ProductDB.asin == asin).first()
        except SQLAlchemyError as e:
            print(f"Error getting product data: {e}")


async def get_db():
    db_manager = DatabaseManager(None)
    Session = db_manager.get_session()
    session = Session()
    try:
        yield session
    except SQLAlchemyError as e:
        session.rollback()
        raise InternalError(str(e))
    finally:
        session.close()

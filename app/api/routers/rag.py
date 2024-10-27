from fastapi import APIRouter, Depends
import pandas as pd
from sqlalchemy.orm import Session

from ..exceptions import NotFoundError
from database import ProductDB, get_db
from rag.pipeline import WeaviateManager
from rag.chatbot import OpenAIChatbot


router = APIRouter(prefix="/rag")

weaviate_manager = WeaviateManager()
openai_chatbot = OpenAIChatbot("gpt-3.5-turbo")


async def fetch_data(db: Session):
    products = db.query(ProductDB).all()
    if not products:
        raise NotFoundError("Products", "No products found in the database.")
    return pd.DataFrame(
        [
            {
                "id": p.id,
                "title": p.title,
                "brand": p.brand,
                "model": p.model,
                "price": p.price,
                "average_rating": p.average_rating,
                "review_count": p.review_count,
            }
            for p in products
        ]
    )


@router.post("/initialize")
async def initialize_weaviate(db: Session = Depends(get_db)):
    df = await fetch_data(db)
    weaviate_manager.initialize_schema()
    weaviate_manager.add_data(df)
    return {"message": "Weaviate initialized with product data."}


@router.post("/query")
async def query_rag(question: str):
    results = weaviate_manager.query(question)
    print(results)
    context_items = []
    for o in results.objects:
        print(o.properties)
        print(o.metadata.creation_time)
        if o.properties:
            context_items.append(
                f"{o.properties['title']} - {o.properties['brand']} ({o.properties['model']}): ${o.properties['price']} | Rating: {o.properties['average_rating']} | Reviews: {o.properties['review_count']}"
            )
    context = "\n".join(context_items)
    print(context)

    response = openai_chatbot.ask_question(question, context)
    return {"response": response}

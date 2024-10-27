import pandas as pd
import math

import weaviate
from weaviate.classes.config import Property, DataType, Tokenization
from weaviate.classes.config import Configure, VectorDistances
from weaviate.classes.query import MetadataQuery


def valid_or_default(value, default):
    return (
        value
        if value is not None and not (isinstance(value, float) and math.isnan(value))
        else default
    )


class WeaviateManager:
    def __init__(self):
        self.client = weaviate.connect_to_local(port=8080)

    def initialize_schema(self):
        try:
            # Clear up the schema, so that we can recreate it
            if self.client.collections.exists("Product"):
                self.client.collections.delete("Product")

            self.client.collections.create(
                name="Product",
                vectorizer_config=Configure.Vectorizer.text2vec_openai(),
                # vector_index_config=Configure.VectorIndex.hnsw(
                #     distance_metric=VectorDistances.COSINE
                # ),
                properties=[
                    Property(
                        name="title",
                        data_type=DataType.TEXT,
                        # vectorize_property_name=True,
                        # tokenization=Tokenization.WHITESPACE,
                    ),
                    Property(
                        name="brand",
                        data_type=DataType.TEXT,
                        # vectorize_property_name=True,
                        # tokenization=Tokenization.LOWERCASE,
                    ),
                    Property(
                        name="model",
                        data_type=DataType.TEXT,
                        # vectorize_property_name=False,
                    ),
                    Property(
                        name="price",
                        data_type=DataType.NUMBER,
                        # vectorize_property_name=False,
                    ),
                    Property(
                        name="average_rating",
                        data_type=DataType.NUMBER,
                        # vectorize_property_name=False,
                    ),
                    Property(
                        name="review_count",
                        data_type=DataType.INT,
                        # vectorize_property_name=False,
                    ),
                ],
            )

            products = self.client.collections.get("Product")
            products_config = products.config.get()
            print(products_config)

        except Exception as e:
            print(f"Class creation error: {str(e)}")

    def close(self):
        self.client.close()

    def add_data(self, df: pd.DataFrame):
        collection = self.client.collections.get("Product")
        with collection.batch.dynamic() as batch:
            for _, row in df.iterrows():
                data_obj = {
                    "title": valid_or_default(row.get("title"), "Unknown Title"),
                    "brand": valid_or_default(row.get("brand"), "Unknown Brand"),
                    "model": valid_or_default(row.get("model"), "Unknown Model"),
                    "price": valid_or_default(row.get("price"), 0.0),
                    "average_rating": valid_or_default(row.get("average_rating"), 0.0),
                    "review_count": valid_or_default(row.get("review_count"), 0),
                }
                print(data_obj)
                batch.add_object(
                    properties=data_obj,
                )

    def query(self, question: str):
        collection = self.client.collections.get("Product")
        results = collection.query.near_text(
            query=question, limit=3, return_metadata=MetadataQuery(distance=True)
        )
        return results

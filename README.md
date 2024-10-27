# Amazon Analytics Platform

A comprehensive analytics platform for scraping, analyzing, and serving products data from Amazon. This project includes web scraping capabilities, a REST API, and a RAG-based conversational AI system for data insights.


## 🚀 Features

- **Web Scraping**
  - Automated scraping of products from Amazon
  - Collects detailed product information and user reviews
  - Scheduled scraping with configurable intervals
  - Data persistence in PostgreSQL

- **REST API**
  - Built with FastAPI for high performance
  - Comprehensive product search and filtering
  - Review management
  - Pagination support
  - Top products analytics

- **AI Insights**
  - RAG (Retrieval Augmented Generation) system
  - Conversational interface for data analysis
  - Built on Weaviate with OpenAI integration


## 🛠️ Tech Stack

- **Backend**: Python 3.9+, FastAPI
- **Database**: PostgreSQL, SQLAlchemy
- **Scraping**: Playwright, BeautifulSoup4
- **AI/ML**: Transformers, Weaviate, OpenAI
- **DevOps**: Docker
- **Testing**: pytest


## 📚 Project Structure

```bash
amazon_products_analytics/
├── app/
│   ├── api/
│   │   ├── routers/
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   └── response_models.py
│   ├── scraper/
│   │   ├── amazon_scraper.py
│   │   └── scheduler.py
│   ├── rag/
│   │   ├── chatbot.py
│   │   └── pipeline.py
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   └── database.py
├── scripts/
├── tests/
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```


## 🔧 Installation

### 📋 Prerequisites

- Python 3.9 or higher
- Docker
- PostgreSQL
- OpenAI API key
- Weaviate
- Chrome WebDriver

### Steps

1. Clone the repository:
```bash
git clone https://github.com/abir0/amazon-products-analytics.git
cd amazon-products-analytics
```

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

1. Install dependencies:
```bash
pip install -r requirements.txt
```

1. Configure environment variables in `.env` file in the root directory.


5. Set up PostgreSQL:
```bash
psql -U postgres -f scripts/init_db.sql
```

6. Start the services using Docker Compose:
```bash
docker-compose up -d
```


## 📋 Usage

### Starting the API Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`

### Running the Scraper

```bash
python -m app.scraper.scheduler
```

### Using the RAG System

```python
from app.llm.rag import AnalyticsRAG

rag = AnalyticsRAG(db_session, openai_api_key)
response = rag.query("What are the top-rated watches under $500?")
```

## 🔌 API Endpoints

- **GET /products**: Search, filter, and sort products.
  - Query params: `brand`, `min_price`, `max_price`, `page`, `limit`, `sort_by`
  - Example: `GET /products?brand=Seiko&min_price=100&max_price=500&page=1&limit=10`

- **GET /products/top**: Retrieve top-rated products based on reviews.
  - Example: `GET /products/top`

- **GET /products/{product_id}/reviews**: Get reviews for a specific product.
  - Query params: `page`, `limit`
  - Example: `GET /products/123/reviews?page=1&limit=5`


## 📦 Cloud Deployment

The project is containerized and can be deployed to any cloud provider that supports Docker containers.

Here's how to deploy using AWS:

### AWS

1. **API & Scraping Service**: 
   - **EC2** for hosting the FastAPI app.
   - **ECS** for container orchestration
   - **AWS Lambda** can schedule periodic scraping tasks.

2. **Database**: 
   - **Amazon RDS** for PostgreSQL database.

3. **AI Model**:
   - **SageMaker** for deploying the LLM model as an API endpoint.

4. **Storage**: 
   - **S3** for storing scraped product images.

5. **Monitoring**:
   - **CloudWatch** for logs and performance monitoring of the services.


## 👨🏻‍💻 Author

Created by Abir.

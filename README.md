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
│   ├── frontend/
│   │   ├── static/
│   │   ├── __init__.py
│   │   └── app.py
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

1. Set up PostgreSQL database named `amazon_products`.
```bash
sudo -u postgres psql
CREATE DATABASE amazon_products;
\q
```

1. Start the weaviate database using Docker Compose:
```bash
cd app/rag
docker compose up -d
cd -
```

1. Start the backend app:
```bash
python3 app/app.py
```

1. Start the frontend app:
```bash
streamlit run app/frontend/app.py
```


## 📋 Usage

### Starting the API Server

```bash
python3 app/app.py
```

The API will be available at `http://localhost:8001`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8001/docs`

### Running the Scraper

```bash
python3 app/app.py
```

### Using the RAG System

```bash
curl -X 'POST' \
  'http://localhost:8001/rag/query?question=hi' \
  -H 'accept: application/json' \
  -d ''
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

Here's my way of deploying this app using AWS:

### AWS

1. **API & Scraping Service**: 
   - **EC2** for hosting the FastAPI app. EC2 is the fully-managed service so its really customizable.
   - **ECS** for container orchestration. This will be useful when there's a lot of different products to scrape.

2. **Database**: 
   - **Amazon RDS** for PostgreSQL database. This is one of the most versatile DB services as it can be useful to migrate into a different open-source databases later on. It is also very configurable. Such as if we need to sync with other DB such as Elasticsearch, we can readily configure it.

3. **AI Model**:
   - **SageMaker** for deploying the LLM model as an API endpoint. This can be auto-scaled so deploying fine-tuned models from SageMaker can be really easy. Also we can setup custom training and evaluation pipeline through this service.

4. **Storage**: 
   - **S3** for storing scraped product images. S3 offers different tiers of persistence of the storage. So, this is a must for storing images and using CloudFront or CDN's to make the access time tailored to specific zones.

5. **Monitoring**:
   - **CloudWatch** for logs and performance monitoring of the services.


## 👨🏻‍💻 Author

Created by [Abir](https://www.linkedin.com/in/abir0/).

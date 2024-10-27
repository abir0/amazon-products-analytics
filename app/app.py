from datetime import datetime
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.routers import products
from api.routers import scheduler
from api.routers import rag
from api.exceptions import APIError
from api.exceptions import api_error_handler, general_error_handler
from config import get_config
from main import main
from scraper.scheduler import job_scheduler


config = get_config()

app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    swagger_ui_parameters={
        "docExpansion": "none",
        "syntaxHighlight.theme": "obsidian",
    },
)

app.include_router(products.router)
app.include_router(scheduler.router)
app.include_router(rag.router)

# Register exception handlers on the app
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(Exception, general_error_handler)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next: callable) -> dict:
    start_time = perf_counter()
    response = await call_next(request)
    process_time = perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Scheduler management
@app.on_event("startup")
async def startup_event():
    try:
        # Add the job to the scheduler
        job_scheduler.add_job(
            main,
            "interval",
            days=3,
            id="product_scraping_job",
            replace_existing=True,
            next_run_time=datetime.now(),
        )

        # Start the scheduler
        job_scheduler.start()
        print("Successfully started the scheduler")

    except Exception as e:
        print(f"Failed to start scheduler: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    try:
        # Shut down the scheduler gracefully
        job_scheduler.shutdown(wait=True)
        print("Successfully shut down the scheduler")

    except Exception as e:
        print(f"Error during scheduler shutdown: {str(e)}")
        raise


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=8001, reload=False)

import asyncio
import concurrent.futures
from time import perf_counter

from config import get_config
from database import DatabaseManager
from models import Product
from scraper.amazon_scraper import AmazonScraper


config = get_config()


class DataLoader:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def load_product(self, product_data):
        try:
            product = Product(**product_data)
            return self.db_manager.create_product(product.model_dump())
        except Exception as e:
            print(f"Error loading product data: {e}")
            return None


async def process_product(scraper, loader, url):
    product_data = await scraper.scrape_product_data(url)
    if product_data:
        return loader.load_product(product_data)


def get_product_urls(scraper, keyword, max_pages) -> list:
    return asyncio.run(scraper.get_product_urls(keyword, max_pages=max_pages))


def run_scraper(scraper, loader, url):
    asyncio.run(process_product(scraper, loader, url))


def run_jobs(urls: list, scraper: callable, loader: callable) -> None:
    start = perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {
            executor.submit(run_scraper, scraper, loader, url): url for url in urls
        }
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
                print(f"Successfully processed URL: {url}")
            except Exception as e:
                print(f"Error during scraping for {url}: {e}")
    end = perf_counter()
    print(f"Time taken: {(end - start) / 60} minutes")


def main(keyword="watch", max_pages=2):
    db_manager = DatabaseManager(None)
    scraper = AmazonScraper()
    loader = DataLoader(db_manager)

    product_urls = get_product_urls(scraper, keyword, max_pages)
    run_jobs(product_urls, scraper, loader)


if __name__ == "__main__":
    main()

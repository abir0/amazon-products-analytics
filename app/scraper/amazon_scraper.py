import asyncio
from datetime import datetime
from functools import wraps
import random
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


def handle_exceptions(func):
    """Decorator to handle exceptions in extraction methods."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return None

    return wrapper


class WebClient:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    ]

    def __init__(
        self,
        ua_rotation=False,
        timeout: int = 10000,
        wait_until: str = "domcontentloaded",
        headless: bool = True,
    ):
        self.user_agents = self.USER_AGENTS
        self.ua_rotation = ua_rotation
        self.timeout = timeout
        self.wait_until = wait_until
        self.headless = headless
        self.browser = None
        self.page = None

    async def initialize_browser(self):
        playwright = await async_playwright().start()
        launch_options = {"headless": self.headless}

        self.browser = await playwright.chromium.launch(**launch_options)
        user_agent = (
            random.choice(self.user_agents) if self.ua_rotation else self.user_agents[0]
        )
        context = await self.browser.new_context(user_agent=user_agent)
        self.page = await context.new_page()

    async def close_browser(self):
        if self.browser:
            await self.browser.close()

    async def get_page_source(self, url: str) -> BeautifulSoup:
        await self.page.goto(url, wait_until=self.wait_until)
        await self.page.wait_for_timeout(self.timeout)
        html_content = await self.page.content()
        return BeautifulSoup(html_content, "html.parser")


class AmazonScraper:
    def __init__(self):
        self.base_url = "https://www.amazon.com"
        self.client = WebClient()

    async def get_product_urls(self, keyword: str, max_pages: int = 10) -> List[str]:
        """Get product URLs based on a search keyword."""
        await self.client.initialize_browser()
        search_url = f"{self.base_url}/s?k={keyword.replace(' ', '+')}"
        product_urls = []

        for page in range(1, max_pages + 1):
            page_url = f"{search_url}&page={page}"
            soup = await self.client.get_page_source(page_url)
            products = soup.find_all("div", {"data-cy": "title-recipe"})
            if len(products) == 0:
                print(f"No products found on page {page}. Stopping pagination.")
                break
            for product in products:
                try:
                    href = product.find("a").get("href").split("/ref=")[0]
                    if self.extract_asin(href):
                        product_url = urljoin(self.base_url, href)
                        product_urls.append(product_url)
                except Exception as e:
                    print(f"Error processing product link: {e}")

            # Random delay
            await asyncio.sleep(random.uniform(1, 3))

        await self.client.close_browser()
        product_urls = list(set(product_urls))
        print(f"Found {len(product_urls)} product URLs.")
        return product_urls

    async def scrape_product_data(self, product_url: str) -> Dict[str, any]:
        """Scrape product data from a given product URL."""
        await self.client.initialize_browser()
        soup = await self.client.get_page_source(product_url)
        await self.client.close_browser()

        # Extract product details
        asin = self.extract_asin(product_url)
        title = self.extract_title(soup)
        price = self.extract_price(soup)
        rating = self.extract_rating(soup)
        review_count = self.extract_review_count(soup)
        top_reviews = self.extract_top_reviews(soup)
        specs = self.extract_technical_specs(soup)
        images = self.extract_image_urls(soup)

        return {
            "asin": asin,
            "product_url": product_url,
            "brand": specs.get("Brand, Seller, or Collection Name"),
            "model": specs.get("Model number"),
            "title": title,
            "price": price,
            "average_rating": rating,
            "review_count": review_count,
            "specifications": specs,
            "image_urls": images,
            "top_reviews": top_reviews,
        }

    @staticmethod
    @handle_exceptions
    def extract_asin(url: str) -> str:
        match = re.search(r"/dp/([A-Z0-9]{10})", url)
        return match.group(1)

    @staticmethod
    @handle_exceptions
    def extract_title(soup: BeautifulSoup) -> Optional[str]:
        return soup.find(id="productTitle").get_text(strip=True)

    @staticmethod
    @handle_exceptions
    def extract_price(soup: BeautifulSoup) -> Optional[float]:
        price_str = (
            soup.find(id="corePriceDisplay_desktop_feature_div")
            .find("span", {"aria-hidden": "true"})
            .get_text(strip=True)
        )
        return float(price_str.replace(",", "").replace("$", ""))

    @staticmethod
    @handle_exceptions
    def extract_rating(soup: BeautifulSoup) -> Optional[float]:
        rating_str = (
            soup.find(id="acrPopover")
            .find("span", {"class": "a-size-base a-color-base"})
            .get_text(strip=True)
        )
        return float(rating_str)

    @staticmethod
    @handle_exceptions
    def extract_review_count(soup: BeautifulSoup) -> Optional[int]:
        review_count_str = (
            soup.find(id="acrCustomerReviewText").get_text(strip=True).split(" ")[0]
        )
        return int(review_count_str.replace(",", ""))

    @staticmethod
    def extract_top_reviews(soup: BeautifulSoup) -> List[Dict[str, str]]:
        reviews = []
        for review in soup.find_all("div", {"data-hook": "review"}):
            try:
                item = {}

                # Reviewer name
                item["name"] = review.find(
                    "span", {"class": "a-profile-name"}
                ).get_text(strip=True)

                # Rating by reviewer
                item["rating"] = int(
                    float(
                        review.find("i", {"data-hook": "review-star-rating"})
                        .get_text()
                        .replace("out of 5 stars", "")
                        .strip()
                    )
                )

                # Review date
                item["date"] = Utilities.extract_date(
                    review.find("span", {"data-hook": "review-date"}).get_text()
                )

                # Review body text
                item["text"] = review.find(
                    "span", {"data-hook": "review-body"}
                ).get_text(strip=True)

                reviews.append(item)
            except Exception:
                continue
        return reviews

    @staticmethod
    def extract_technical_specs(soup: BeautifulSoup) -> Dict[str, str]:
        specs = {}
        try:
            table = soup.find("table", {"id": "technicalSpecifications_section_1"})
            specs = {
                row.th.get_text(strip=True): row.td.get_text(" ", strip=True)
                for row in table.find_all("tr")
            }
        except Exception as e:
            print(f"Error extracting technical specs: {e}")
        return specs

    @staticmethod
    def extract_image_urls(soup: BeautifulSoup) -> List[str]:
        image_urls = []
        try:
            images = [
                img.get("src") for img in soup.find(id="altImages").find_all("img")
            ]
            image_urls = Utilities.clean_image_urls(Utilities.filter_image_urls(images))
        except Exception as e:
            print(f"Error extracting image URLs: {e}")
        return image_urls


class Utilities:
    @staticmethod
    def filter_image_urls(urls: List[str]) -> List[str]:
        pattern = r"^https://m\.media\-amazon\.com/images/I/.{,26}\.jpg$"
        return [url for url in urls if re.match(pattern, url)]

    @staticmethod
    def clean_image_urls(urls: List[str]) -> List[str]:
        return [re.sub(r"\._AC_SR\d{2,3},\d{2,3}_\.jpg", ".jpg", url) for url in urls]

    @staticmethod
    def extract_date(text: str) -> Optional[datetime]:
        match = re.search(r"on (\w+ \d{1,2}, \d{4})", text)
        return datetime.strptime(match.group(1), "%B %d, %Y") if match else None


async def test_run():
    scraper = AmazonScraper()
    product_urls = await scraper.get_product_urls("watch", max_pages=2)

    for i, url in enumerate(product_urls):
        print(f"Scraping product {i + 1} / {len(product_urls)}")
        product_data = await scraper.scrape_product_data(url)
        print(product_data)
        if i == 2:
            break


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_run())

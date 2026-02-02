"""
GreenValley Scraper
Scrapes product data from greenvalley.pk using Shopify JSON API
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional
from base_scraper import BaseScraper
from datetime import datetime


class GreenValleyScraper(BaseScraper):
    """Scraper for GreenValley Pakistan using Shopify JSON API"""
    
    def __init__(self, output_dir: str = "data"):
        super().__init__(
            store_name="GreenValley",
            base_url="https://greenvalley.pk",
            output_dir=output_dir
        )
    
    async def fetch_page(self, session: aiohttp.ClientSession, page: int) -> List[Dict]:
        """Fetch a single page of products from the JSON API"""
        url = f"{self.base_url}/collections/all/products.json"
        params = {
            'limit': 250,
            'page': page
        }
        
        try:
            async with session.get(url, params=params, timeout=30) as response:
                if response.status != 200:
                    self.logger.error(f"Failed to fetch page {page}: Status {response.status}")
                    return []
                
                data = await response.json()
                return data.get('products', [])
        except Exception as e:
            self.logger.error(f"Error fetching page {page}: {e}")
            return []

    async def get_categories(self) -> List[Dict]:
        """Shopify collections can be used as categories"""
        return [{'name': 'All Products', 'url': f"{self.base_url}/collections/all"}]

    async def scrape(self) -> List[Dict]:
        """Main entry point for scraping"""
        all_products = []
        page = 1
        
        async with aiohttp.ClientSession(headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }) as session:
            while True:
                self.logger.info(f"Fetching page {page}...")
                products = await self.fetch_page(session, page)
                
                if not products:
                    self.logger.info("Reached end of products or failed to fetch")
                    break
                
                for item in products:
                    variants = item.get('variants', [])
                    if not variants:
                        continue
                        
                    variant = variants[0]
                    price = self._clean_price(variant.get('price'))
                    disc_price = self._clean_price(variant.get('compare_at_price'))
                    
                    product_url = f"{self.base_url}/products/{item.get('handle')}"
                    
                    images = item.get('images', [])
                    image_url = images[0].get('src') if images else None
                    
                    unit, quantity = self._parse_unit_quantity(item.get('title', ''))
                    
                    tags = item.get('tags', [])
                    category = item.get('product_type', 'General')
                    
                    product = self.create_product_dict(
                        product_name=item.get('title'),
                        price=price,
                        discounted_price=disc_price if disc_price and disc_price != price else None,
                        url=product_url,
                        image_url=image_url,
                        brand=item.get('vendor'),
                        category=category,
                        unit=unit,
                        quantity=quantity
                    )
                    
                    if self.validate_product(product):
                        all_products.append(product)
                
                self.logger.info(f"✓ Page {page}: Extracted {len(products)} products")
                page += 1
                
                if page > 100:
                    break
                    
                await asyncio.sleep(1)
                
        self.logger.info(f"✓ Total GreenValley products: {len(all_products)}")
        return all_products

async def main():
    scraper = GreenValleyScraper()
    products = await scraper.scrape()
    if products:
        scraper.save_to_csv(products)

if __name__ == "__main__":
    asyncio.run(main())

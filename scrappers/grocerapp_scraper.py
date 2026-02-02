"""
GrocerApp Scraper
Scrapes product data from grocerapp.pk with infinite scroll support
"""

import asyncio
from playwright.async_api import async_playwright
from typing import List, Dict, Optional
from base_scraper import BaseScraper
import json


class GrocerAppScraper(BaseScraper):
    """Scraper for GrocerApp Pakistan"""
    
    def __init__(self, output_dir: str = "data"):
        super().__init__(
            store_name="GrocerApp",
            base_url="https://grocerapp.pk",
            output_dir=output_dir
        )
        self.playwright = None
        self.browser = None
        self.context = None
    
    async def setup_browser(self):
        """Initialize Playwright browser"""
        self.logger.info("Initializing browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.logger.info("✓ Browser initialized")
    
    async def close_browser(self):
        """Close browser and cleanup"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.logger.info("✓ Browser closed")
    
    async def scroll_to_bottom(self, page):
        """Scroll to bottom to trigger infinite load"""
        self.logger.info("Scrolling to load products...")
        
        last_height = await page.evaluate("document.body.scrollHeight")
        while True:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3) # Wait for load
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
            # Stop if we have enough products (safety)
            count = await page.locator(".MuiCard-root").count()
            if count > 500: # Limit per category for now
                break
        
        self.logger.info(f"✓ Scrolling finished. Approx {await page.locator('.MuiCard-root').count()} products visible.")

    async def get_categories(self) -> List[Dict]:
        """Extract categories from the sidebar or main menu"""
        self.logger.info("Extracting categories...")
        page = await self.context.new_page()
        try:
            await page.goto(f"{self.base_url}/categories", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(2)
            
            # Look for subcategory links (they have an image and a name in a grid)
            categories = await page.evaluate('''() => {
                const cats = [];
                // Target the links that contain category names and images
                document.querySelectorAll('a[href]').forEach(a => {
                    const nameEl = a.querySelector('p');
                    const name = nameEl ? nameEl.innerText.trim() : '';
                    const url = a.href;
                    
                    // Filter for likely category links (usually short paths, not main pages)
                    const path = a.getAttribute('href');
                    if (name && path && path.length > 1 && !path.includes('categories') && !path.includes('cart') && !path.includes('login')) {
                        if (!cats.find(c => c.url === url)) {
                            cats.push({ name, url });
                        }
                    }
                });
                return cats;
            }''')
            
            self.logger.info(f"✓ Found {len(categories)} categories")
            return categories
        except Exception as e:
            self.logger.error(f"Error getting categories: {e}")
            return []
        finally:
            await page.close()

    async def scrape_category(self, category: Dict) -> List[Dict]:
        """Scrape products from a specific category page"""
        self.logger.info(f"Scraping category: {category['name']}")
        page = await self.context.new_page()
        products = []
        
        try:
            await page.goto(category['url'], wait_until="networkidle", timeout=60000)
            await asyncio.sleep(2)
            
            # Scroll to load all
            await self.scroll_to_bottom(page)
            
            # Extract basic product data
            cards = await page.evaluate('''() => {
                const results = [];
                document.querySelectorAll('.MuiCard-root').forEach(card => {
                    const nameEl = card.querySelector('.MuiTypography-body1');
                    const priceEl = card.querySelector('.MuiTypography-subtitle2');
                    const name = nameEl ? nameEl.innerText.trim() : null;
                    const priceText = priceEl ? priceEl.innerText.trim() : null;
                    const imgEl = card.querySelector('img');
                    const img = imgEl ? imgEl.src : null;
                    const linkEl = card.querySelector('a');
                    const url = linkEl ? linkEl.href : null;
                    
                    if (name && priceText) {
                        results.push({ name, priceText, img, url });
                    }
                });
                return results;
            }''')
            
            for card in cards:
                price = self._clean_price(card['priceText'])
                if price is None:
                    continue
                
                unit, quantity = self._parse_unit_quantity(card['name'])
                
                product = self.create_product_dict(
                    product_name=card['name'],
                    price=price,
                    url=card['url'],
                    image_url=card['img'],
                    category=category['name'],
                    unit=unit,
                    quantity=quantity
                )
                
                if self.validate_product(product):
                    products.append(product)
            
            self.logger.info(f"✓ Extracted {len(products)} products from {category['name']}")
            return products
        except Exception as e:
            self.logger.error(f"Error scraping category {category['name']}: {e}")
            return []
        finally:
            await page.close()

    async def scrape(self) -> List[Dict]:
        """Main entry point for scraping"""
        all_products = []
        try:
            await self.setup_browser()
            categories = await self.get_categories()
            
            # Prioritize some main grocery categories
            priorities = ["Beverages", "Milk & Dairy", "Grains & Pulses", "Oil & Ghee", "Snacks"]
            
            for category in categories:
                # Optional: Filter or limit for testing
                products = await self.scrape_category(category)
                all_products.extend(products)
                
                # Check for duplicates or limit
                if len(all_products) > 10000:
                    break
                    
                await asyncio.sleep(2) # Rate limiting
            
            self.logger.info(f"✓ Total GrocerApp products: {len(all_products)}")
        except Exception as e:
            self.logger.error(f"Scraper error: {e}")
        finally:
            await self.close_browser()
            
        return all_products

async def main():
    scraper = GrocerAppScraper()
    products = await scraper.scrape()
    if products:
        scraper.save_to_csv(products)

if __name__ == "__main__":
    asyncio.run(main())

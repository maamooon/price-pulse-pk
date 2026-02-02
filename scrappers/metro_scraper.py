"""
Metro Online Pakistan Scraper
Scrapes product data from metro-online.pk with lazy-loading support
"""

import asyncio
from playwright.async_api import async_playwright
from typing import List, Dict, Optional
from base_scraper import BaseScraper


class MetroScraper(BaseScraper):
    """Scraper for Metro Online Pakistan"""
    
    def __init__(self, output_dir: str = "data"):
        super().__init__(
            store_name="Metro",
            base_url="https://www.metro-online.pk",
            output_dir="../data"
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
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
    
    async def scroll_to_load_all_products(self, page):
        """Scroll to bottom to load all lazy-loaded products"""
        self.logger.info("Scrolling to load all products...")
        previous_height = 0
        scroll_attempts = 0
        max_scroll_attempts = 15
        no_change_count = 0
        
        while scroll_attempts < max_scroll_attempts:
            # Scroll to bottom
            current_height = await page.evaluate('''() => {
                window.scrollTo(0, document.body.scrollHeight);
                return document.body.scrollHeight;
            }''')
            
            await asyncio.sleep(2)
            
            # Check for load more button
            load_more_selectors = [
                'button:has-text("Load More")',
                'button:has-text("Show More")',
                '.load-more'
            ]
            
            for selector in load_more_selectors:
                try:
                    load_more_btn = await page.query_selector(selector)
                    if load_more_btn and await load_more_btn.is_visible():
                        await load_more_btn.click()
                        await asyncio.sleep(3)
                        break
                except:
                    continue
            
            # Check if reached bottom
            if current_height == previous_height:
                no_change_count += 1
                if no_change_count >= 2:
                    break
            else:
                no_change_count = 0
            
            previous_height = current_height
            scroll_attempts += 1
            
            # Count products
            product_count = await page.evaluate('''() => {
                return document.querySelectorAll('.CategoryGrid_product_card__FUMXW').length;
            }''')
            
            if scroll_attempts % 3 == 0:
                self.logger.info(f"Scroll {scroll_attempts}: {product_count} products loaded")
        
        self.logger.info(f"✓ Finished scrolling after {scroll_attempts} attempts")
    
    async def get_categories(self) -> List[Dict]:
        """Extract all main categories from homepage"""
        self.logger.info("Extracting main categories...")
        
        page = await self.context.new_page()
        await page.goto(f"{self.base_url}/home", wait_until='networkidle', timeout=45000)
        await page.wait_for_selector('.CategoryGrid_grid_container__ouyHW', timeout=15000)
        
        categories = await page.evaluate('''() => {
            const categories = [];
            const categoryElements = document.querySelectorAll('.CategoryGrid_grid_item__FXimL');
            
            categoryElements.forEach((element) => {
                const linkElement = element.querySelector('a');
                const imgElement = element.querySelector('img');
                
                if (linkElement && imgElement) {
                    categories.push({
                        name: imgElement.alt || 'No name',
                        url: linkElement.href || 'No URL',
                        image_url: imgElement.src || 'No image'
                    });
                }
            });
            
            return categories;
        }''')
        
        await page.close()
        self.logger.info(f"✓ Found {len(categories)} main categories")
        return categories
    
    async def get_subcategories(self, category: Dict) -> List[Dict]:
        """Extract sub-categories for a main category"""
        self.logger.info(f"Getting subcategories for {category['name']}...")
        
        page = await self.context.new_page()
        
        try:
            await page.goto(category['url'], wait_until='networkidle', timeout=45000)
            
            # Try to find subcategory container
            sub_category_selector = '.sc-gKPRtg.jJzJeK'
            
            try:
                await page.wait_for_selector(sub_category_selector, timeout=5000)
            except:
                # No subcategories, return main category as single item
                await page.close()
                return [{
                    'name': category['name'],
                    'url': category['url'],
                    'main_category': category['name']
                }]
            
            subcategories = await page.evaluate('''(selector) => {
                const subCats = [];
                const container = document.querySelector(selector);
                
                if (container) {
                    const links = container.querySelectorAll('a');
                    links.forEach((link) => {
                        const imgElement = link.querySelector('img');
                        const nameElement = link.querySelector('h6, .sc-cwSeag');
                        
                        if (link.href && nameElement) {
                            subCats.push({
                                name: nameElement.textContent?.trim() || 'No name',
                                url: link.href,
                                image_url: imgElement?.src || 'No image'
                            });
                        }
                    });
                }
                return subCats;
            }''', sub_category_selector)
            
            # Add main category info
            for subcat in subcategories:
                subcat['main_category'] = category['name']
            
            await page.close()
            self.logger.info(f"✓ Found {len(subcategories)} subcategories")
            return subcategories
            
        except Exception as e:
            self.logger.error(f"Error getting subcategories: {e}")
            await page.close()
            return []
    
    async def scrape_subcategory_products(self, subcategory: Dict) -> List[Dict]:
        """Scrape all products from a subcategory"""
        self.logger.info(f"Scraping products from {subcategory['name']}...")
        
        page = await self.context.new_page()
        products = []
        
        try:
            await page.goto(subcategory['url'], wait_until='networkidle', timeout=45000)
            
            # Wait for products
            try:
                await page.wait_for_selector('.CategoryGrid_product_card__FUMXW', timeout=10000)
            except:
                self.logger.warning(f"No products found in {subcategory['name']}")
                await page.close()
                return []
            
            # Scroll to load all products
            await self.scroll_to_load_all_products(page)
            await asyncio.sleep(2)
            
            # Extract products
            raw_products = await page.evaluate('''() => {
                const products = [];
                const productElements = document.querySelectorAll('.CategoryGrid_product_card__FUMXW');
                
                productElements.forEach((productEl) => {
                    const nameElement = productEl.querySelector('.CategoryGrid_product_name__3nYsN');
                    const priceElement = productEl.querySelector('.CategoryGrid_product_price__Svf8T');
                    const linkElement = productEl.querySelector('a[href*="/detail/"]');
                    const imgElement = productEl.querySelector('img');
                    const badgeElement = productEl.querySelector('[data-after-content]');
                    
                    const productUrl = linkElement?.href || '';
                    const urlParts = productUrl.split('/');
                    const productId = urlParts[urlParts.length - 1] || '';
                    
                    products.push({
                        id: productId,
                        name: nameElement?.textContent?.trim() || '',
                        price: priceElement?.textContent?.trim() || '',
                        url: productUrl,
                        image_url: imgElement?.src || '',
                        badge: badgeElement?.getAttribute('data-after-content') || null
                    });
                });
                
                return products;
            }''')
            
            # Process each product
            for raw_product in raw_products:
                if not raw_product['name'] or not raw_product['price']:
                    continue
                
                # Clean price
                price = self._clean_price(raw_product['price'])
                if price is None:
                    continue
                
                # Parse unit and quantity from product name
                unit, quantity = self._parse_unit_quantity(raw_product['name'])
                
                # Check for discount (badge might indicate sale)
                discounted_price = None
                if raw_product['badge'] and 'sale' in raw_product['badge'].lower():
                    # Price shown is already discounted
                    discounted_price = price
                
                product = self.create_product_dict(
                    product_name=raw_product['name'],
                    price=price,
                    url=raw_product['url'],
                    image_url=raw_product['image_url'],
                    category=subcategory['main_category'],
                    subcategory=subcategory['name'] if subcategory['name'] != subcategory['main_category'] else None,
                    discounted_price=discounted_price,
                    unit=unit,
                    quantity=quantity
                )
                
                if self.validate_product(product):
                    products.append(product)
            
            await page.close()
            self.logger.info(f"✓ Scraped {len(products)} products from {subcategory['name']}")
            
        except Exception as e:
            self.logger.error(f"Error scraping {subcategory['name']}: {e}")
            await page.close()
        
        return products
    
    async def scrape(self) -> List[Dict]:
        """Main scraping method"""
        all_products = []
        
        try:
            await self.setup_browser()
            
            # Get all categories
            categories = await self.get_categories()
            
            # Get subcategories for each category
            all_subcategories = []
            for category in categories:
                subcategories = await self.get_subcategories(category)
                all_subcategories.extend(subcategories)
                await asyncio.sleep(1.5)  # Rate limiting
            
            self.logger.info(f"Total subcategories to scrape: {len(all_subcategories)}")
            
            # Scrape products from each subcategory
            for i, subcategory in enumerate(all_subcategories, 1):
                self.logger.info(f"Progress: {i}/{len(all_subcategories)}")
                products = await self.scrape_subcategory_products(subcategory)
                all_products.extend(products)
                await asyncio.sleep(2)  # Rate limiting
            
            self.logger.info(f"✓ Total products scraped: {len(all_products)}")
            
        except Exception as e:
            self.logger.error(f"Scraping error: {e}")
        finally:
            await self.close_browser()
        
        return all_products


async def main():
    """Run the Metro scraper"""
    scraper = MetroScraper(output_dir="../data")
    
    print("=" * 80)
    print("METRO ONLINE PAKISTAN SCRAPER")
    print("=" * 80)
    
    products = await scraper.scrape()
    
    if products:
        scraper.save_to_csv(products)
        print(f"\n✓ Successfully scraped {len(products)} products from Metro")
        print(f"✓ Data saved to {scraper.output_dir}")
    else:
        print("\n✗ No products were scraped")


if __name__ == "__main__":
    asyncio.run(main())

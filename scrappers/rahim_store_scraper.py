"""
Rahim Store Scraper
Scrapes product data from rahimstore.com with department-based structure
"""

import asyncio
from playwright.async_api import async_playwright
from typing import List, Dict, Optional
from base_scraper import BaseScraper


class RahimStoreScraper(BaseScraper):
    """Scraper for Rahim Store Pakistan"""
    
    def __init__(self, output_dir: str = "data"):
        super().__init__(
            store_name="Rahim Store",
            base_url="https://www.rahimstore.com/department",
            output_dir="../data"
        )
        # Department IDs to scrape
        self.departments = ['001', '002', '003', '004', '005', '006']
        self.playwright = None
        self.browser = None
        self.context = None
    
    async def setup_browser(self):
        """Initialize Playwright browser"""
        self.logger.info("Initializing browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
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
    
    async def wait_for_products_loaded(self, page):
        """Wait for products to be fully loaded"""
        try:
            await page.wait_for_selector('.item.img-hover-zoom--quick-zoom', timeout=20000)
            await asyncio.sleep(2)  # Additional wait for dynamic content
            
            # Check if images and prices loaded
            images = await page.query_selector_all('img.img-fluid[src]')
            prices = await page.query_selector_all('strong')
            
            self.logger.info(f"Loaded {len(images)} images, {len(prices)} prices")
            await asyncio.sleep(1)
            return True
        except Exception as e:
            self.logger.error(f"Error waiting for products: {e}")
            return False
    
    async def extract_product_from_card(self, product_card, department_id: str) -> Optional[Dict]:
        """Extract product information from a product card"""
        try:
            # Product name and URL
            name_element = await product_card.query_selector('a[style="display:block; height:50px;"]')
            if not name_element:
                return None
            
            product_name = await name_element.inner_text()
            product_name = product_name.strip() if product_name else None
            product_url = await name_element.get_attribute('href') or ""
            product_id = await name_element.get_attribute('productid') or ""
            
            # Image
            img_element = await product_card.query_selector('img.img-fluid')
            image_url = await img_element.get_attribute('src') if img_element else None
            
            # Current price
            strong_element = await product_card.query_selector('strong')
            current_price_text = await strong_element.inner_text() if strong_element else None
            if not current_price_text:
                return None
            
            current_price_text = current_price_text.replace('Rs', '').replace('sup', '').strip()
            current_price = self._clean_price(current_price_text)
            
            if current_price is None:
                return None
            
            # Was price (original price if discounted)
            strike_element = await product_card.query_selector('strike')
            was_price_text = await strike_element.inner_text() if strike_element else None
            was_price = self._clean_price(was_price_text) if was_price_text else None
            
            # If was_price exists, current_price is discounted
            discounted_price = current_price if was_price else None
            final_price = was_price if was_price else current_price
            
            # Parse unit and quantity
            unit, quantity = self._parse_unit_quantity(product_name)
            
            product = self.create_product_dict(
                product_name=product_name,
                price=final_price,
                url=product_url if product_url.startswith('http') else f"https://www.rahimstore.com{product_url}",
                image_url=image_url,
                category=f"Department {department_id}",
                subcategory=None,
                discounted_price=discounted_price,
                unit=unit,
                quantity=quantity
            )
            
            return product
            
        except Exception as e:
            self.logger.warning(f"Error extracting product: {e}")
            return None
    
    async def handle_pagination(self, page, current_page: int) -> bool:
        """Check if there's a next page and navigate to it"""
        try:
            await page.wait_for_selector('.pagination', timeout=10000)
            
            # Find next button
            next_button = await page.query_selector('a.page-link[aria-label="Next"]')
            if not next_button:
                return False
            
            # Check if disabled
            is_disabled = await next_button.evaluate('(element) => element.parentElement.classList.contains("disabled")')
            if is_disabled:
                self.logger.info(f"Reached last page ({current_page})")
                return False
            
            # Click next
            self.logger.info(f"Moving to page {current_page + 1}")
            await next_button.click()
            await page.wait_for_timeout(4000)  # Wait for page transition
            await self.wait_for_products_loaded(page)
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Pagination error: {e}")
            return False
    
    async def scrape_department_page(self, page, department_id: str, page_number: int) -> List[Dict]:
        """Scrape all products from a single page"""
        products = []
        
        try:
            if not await self.wait_for_products_loaded(page):
                return []
            
            # Get all product cards
            product_cards = await page.query_selector_all('.item.img-hover-zoom--quick-zoom')
            
            if not product_cards:
                self.logger.warning(f"No products found on page {page_number}")
                return []
            
            self.logger.info(f"Found {len(product_cards)} products on page {page_number}")
            
            # Extract each product
            for i, card in enumerate(product_cards, 1):
                if i % 10 == 0:
                    self.logger.info(f"Progress: {i}/{len(product_cards)}")
                
                product = await self.extract_product_from_card(card, department_id)
                if product and self.validate_product(product):
                    products.append(product)
                
                # Small delay between extractions
                if i > 1:
                    await asyncio.sleep(0.1)
            
            self.logger.info(f"✓ Page {page_number}: Extracted {len(products)} products")
            
        except Exception as e:
            self.logger.error(f"Error scraping page {page_number}: {e}")
        
        return products
    
    async def scrape_department(self, department_id: str) -> List[Dict]:
        """Scrape all pages of a department"""
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"SCRAPING DEPARTMENT {department_id}")
        self.logger.info(f"{'='*80}")
        
        url = f"{self.base_url}/{department_id}"
        all_products = []
        
        page = await self.context.new_page()
        
        try:
            # Navigate to department
            self.logger.info(f"Loading {url}")
            response = await page.goto(url, wait_until='domcontentloaded', timeout=45000)
            
            if not response or response.status != 200:
                self.logger.error(f"Failed to load department {department_id}")
                await page.close()
                return []
            
            # Wait for initial load
            await self.wait_for_products_loaded(page)
            
            # Scrape all pages
            page_number = 1
            max_pages = 100  # Safety limit
            
            while page_number <= max_pages:
                products = await self.scrape_department_page(page, department_id, page_number)
                all_products.extend(products)
                
                # Try to go to next page
                has_next = await self.handle_pagination(page, page_number)
                if not has_next:
                    break
                
                page_number += 1
                await asyncio.sleep(2)  # Rate limiting
            
            self.logger.info(f"✓ Department {department_id}: {len(all_products)} total products")
            
        except Exception as e:
            self.logger.error(f"Error in department {department_id}: {e}")
        finally:
            await page.close()
        
        return all_products
    
    async def scrape(self) -> List[Dict]:
        """Main scraping method"""
        all_products = []
        
        try:
            await self.setup_browser()
            
            # Scrape each department
            for i, dept_id in enumerate(self.departments, 1):
                self.logger.info(f"\nDepartment {i}/{len(self.departments)}")
                products = await self.scrape_department(dept_id)
                all_products.extend(products)
                
                # Pause between departments
                if i < len(self.departments):
                    await asyncio.sleep(5)
            
            self.logger.info(f"✓ Total products scraped: {len(all_products)}")
            
        except Exception as e:
            self.logger.error(f"Scraping error: {e}")
        finally:
            await self.close_browser()
        
        return all_products
    
    async def get_categories(self) -> List[Dict]:
        """Get department categories (for base class compatibility)"""
        return [{"name": f"Department {dept}", "id": dept} for dept in self.departments]


async def main():
    """Run the Rahim Store scraper"""
    scraper = RahimStoreScraper(output_dir="../data")
    
    print("=" * 80)
    print("RAHIM STORE PAKISTAN SCRAPER")
    print("=" * 80)
    
    products = await scraper.scrape()
    
    if products:
        scraper.save_to_csv(products)
        print(f"\n✓ Successfully scraped {len(products)} products from Rahim Store")
        print(f"✓ Data saved to {scraper.output_dir}")
    else:
        print("\n✗ No products were scraped")


if __name__ == "__main__":
    asyncio.run(main())

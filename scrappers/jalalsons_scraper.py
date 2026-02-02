"""
Jalalsons Scraper
Scrapes product data from jalalsons.com.pk with multi-branch support
"""

import asyncio
from playwright.async_api import async_playwright
from typing import List, Dict, Optional
from base_scraper import BaseScraper


class JalalsonsScraper(BaseScraper):
    """Scraper for Jalalsons Pakistan"""
    
    def __init__(self, output_dir: str = "data", target_branch: Optional[str] = None):
        super().__init__(
            store_name="Jalalsons",
            base_url="https://jalalsons.com.pk",
            output_dir="../data"
        )
        self.target_branch = target_branch  # If None, scrape all branches
        self.playwright = None
        self.browser = None
        self.page = None
        
        # Target categories to scrape
        self.target_categories = ["BAKERY", "DELI", "JS ICECREAM", "SWEETS", "DEALS", "GROCERY"]
    
    async def setup_browser(self):
        """Initialize Playwright browser"""
        self.logger.info("Initializing browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.page = await self.browser.new_page()
        self.logger.info("✓ Browser initialized")
    
    async def close_browser(self):
        """Close browser and cleanup"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.logger.info("✓ Browser closed")
    
    async def close_popup(self):
        """Close initial popup if present"""
        try:
            if await self.page.locator("#website_custom_popup").is_visible():
                await self.page.locator('#website_custom_popup .modal-header a.cursor-pointer.ms-auto').click()
                self.logger.info("✓ Popup closed")
        except:
            self.logger.info("No popup found")
    
    async def get_branches(self) -> List[str]:
        """Get all Lahore branches"""
        self.logger.info("Getting branch list...")
        
        # Navigate to homepage
        await self.page.goto(self.base_url, timeout=60000)
        await self.close_popup()
        
        # Click delivery tab
        await self.page.click("a#delivery-loc-tab")
        await self.page.wait_for_selector("#selectDeliveryBranch", timeout=10000)
        
        # Get all branches
        branches = await self.page.locator("#selectDeliveryBranch option").all_text_contents()
        valid_branches = [b for b in branches if "Please select" not in b and "Lahore" in b]
        
        self.logger.info(f"✓ Found {len(valid_branches)} Lahore branches")
        return valid_branches
    
    async def select_branch(self, branch_name: str, is_first: bool = False):
        """Select a specific branch"""
        self.logger.info(f"Selecting branch: {branch_name}")
        
        if is_first:
            # First branch: already on selection page
            await self.page.select_option("#selectDeliveryBranch", label=branch_name)
            await self.page.wait_for_timeout(2000)
            await self.page.click("a#delivery_order")
        else:
            # Subsequent branches: reopen modal
            await self.page.click("a#get_current_loc")
            await self.page.wait_for_selector("#selectDeliveryBranch", timeout=10000)
            await self.page.wait_for_timeout(500)
            await self.page.select_option("#selectDeliveryBranch", label=branch_name)
            await self.page.wait_for_timeout(2000)
            await self.page.click("a#delivery_order")
        
        await self.page.wait_for_selector("ul.navbar-nav", timeout=10000)
        self.logger.info(f"✓ Branch selected: {branch_name}")
    
    async def get_categories(self) -> List[Dict]:
        """Extract category links from navigation"""
        self.logger.info("Extracting categories...")
        
        nav_items = await self.page.locator("ul.navbar-nav > li.nav-item").element_handles()
        category_links = {}
        
        for li in nav_items[:-3]:  # Exclude last 3 items (usually non-product links)
            main_cat = await li.query_selector("a.nav-link")
            main_name = (await main_cat.inner_text()).strip()
            
            if main_name not in self.target_categories:
                continue
            
            await main_cat.hover()
            await self.page.wait_for_timeout(500)
            sub_links = await li.query_selector_all("ul.dropdown-content a")
            
            urls = []
            if sub_links:
                # Has subcategories
                for sub in sub_links:
                    sub_name = (await sub.inner_text()).strip()
                    sub_href = await sub.get_attribute("href")
                    if sub_href:
                        urls.append({
                            "name": sub_name,
                            "url": f"{self.base_url}{sub_href}"
                        })
                category_links[main_name] = urls
            else:
                # No subcategories, use main category
                href = await main_cat.get_attribute("href")
                if href:
                    category_links[main_name] = [{
                        "name": main_name,
                        "url": f"{self.base_url}{href}"
                    }]
        
        # Flatten to list
        all_categories = []
        for main_name, subcats in category_links.items():
            for subcat in subcats:
                all_categories.append({
                    "main_category": main_name,
                    "subcategory": subcat["name"],
                    "url": subcat["url"]
                })
        
        self.logger.info(f"✓ Found {len(all_categories)} categories")
        return all_categories
    
    async def scrape_category_products(self, category: Dict, branch_name: str) -> List[Dict]:
        """Scrape all products from a category"""
        self.logger.info(f"Scraping {category['subcategory']}...")
        products = []
        
        try:
            await self.page.goto(category['url'], timeout=60000)
            await self.page.wait_for_selector(".single_product_theme", timeout=10000)
        except Exception as e:
            self.logger.warning(f"Could not load {category['subcategory']}: {e}")
            return []
        
        # Get all products
        product_elements = await self.page.query_selector_all(".single_product_theme")
        
        for product_el in product_elements:
            try:
                # Extract product details
                name_el = await product_el.query_selector("p.product_name_theme")
                # Attempt to get actual product link from the anchor tag wrapping the name or image
                anchor_el = await product_el.query_selector("a")
                product_url = await anchor_el.get_attribute("href") if anchor_el else category['url']
                if product_url and not product_url.startswith("http"):
                    product_url = f"{self.base_url}{product_url}"
                
                price_el = await product_el.query_selector("span.price-value")
                img_el = await product_el.query_selector("img")
                
                name = (await name_el.inner_text()).strip() if name_el else None
                price_text = (await price_el.inner_text()).strip() if price_el else None
                image = await img_el.get_attribute("src") if img_el else None
                
                if not name or not price_text:
                    continue
                
                # Clean price
                price = self._clean_price(price_text)
                if price is None:
                    continue
                
                # Parse unit and quantity
                unit, quantity = self._parse_unit_quantity(name)
                
                # Determine category structure
                if category['main_category'] == category['subcategory']:
                    cat = category['main_category']
                    subcat = None
                else:
                    cat = category['main_category']
                    subcat = category['subcategory']
                
                product = self.create_product_dict(
                    product_name=name,
                    price=price,
                    url=product_url,
                    image_url=image,
                    brand=None,  # Jalalsons doesn't provide brand separately
                    category=cat,
                    subcategory=subcat,
                    unit=unit,
                    quantity=quantity
                )
                
                # Add branch information to product name or as metadata
                product['product_name'] = f"{name} [{branch_name}]"
                
                if self.validate_product(product):
                    products.append(product)
                    
            except Exception as e:
                self.logger.warning(f"Error extracting product: {e}")
                continue
        
        self.logger.info(f"✓ Scraped {len(products)} products from {category['subcategory']}")
        return products
    
    async def scrape_branch(self, branch_name: str, is_first: bool = False) -> List[Dict]:
        """Scrape all products from a single branch"""
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"SCRAPING BRANCH: {branch_name}")
        self.logger.info(f"{'='*80}")
        
        all_products = []
        
        try:
            # Select branch
            await self.select_branch(branch_name, is_first)
            
            # Get categories
            categories = await self.get_categories()
            
            # Scrape each category
            for i, category in enumerate(categories, 1):
                self.logger.info(f"Category {i}/{len(categories)}")
                products = await self.scrape_category_products(category, branch_name)
                all_products.extend(products)
                await asyncio.sleep(1)  # Rate limiting
            
            self.logger.info(f"✓ Branch {branch_name}: {len(all_products)} products")
            
        except Exception as e:
            self.logger.error(f"Error scraping branch {branch_name}: {e}")
        
        return all_products
    
    async def scrape(self) -> List[Dict]:
        """Main scraping method"""
        all_products = []
        
        try:
            await self.setup_browser()
            
            # Get branches
            branches = await self.get_branches()
            
            # Filter to target branch if specified
            if self.target_branch:
                branches = [b for b in branches if self.target_branch.lower() in b.lower()]
                if not branches:
                    self.logger.error(f"Branch '{self.target_branch}' not found")
                    return []
            
            self.logger.info(f"Will scrape {len(branches)} branch(es)")
            
            # Scrape each branch
            for i, branch in enumerate(branches):
                products = await self.scrape_branch(branch, is_first=(i == 0))
                all_products.extend(products)
                await asyncio.sleep(2)  # Rate limiting between branches
            
            self.logger.info(f"✓ Total products scraped: {len(all_products)}")
            
        except Exception as e:
            self.logger.error(f"Scraping error: {e}")
        finally:
            await self.close_browser()
        
        return all_products


async def main():
    """Run the Jalalsons scraper"""
    # Scrape all branches (can take a while)
    # To scrape specific branch, pass target_branch="Branch Name"
    scraper = JalalsonsScraper(output_dir="../data")
    
    print("=" * 80)
    print("JALALSONS PAKISTAN SCRAPER")
    print("=" * 80)
    
    products = await scraper.scrape()
    
    if products:
        scraper.save_to_csv(products)
        print(f"\n✓ Successfully scraped {len(products)} products from Jalalsons")
        print(f"✓ Data saved to {scraper.output_dir}")
    else:
        print("\n✗ No products were scraped")


if __name__ == "__main__":
    asyncio.run(main())

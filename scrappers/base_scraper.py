"""
Base Scraper Class for Pakistani Grocery Stores
Provides common functionality for all store scrapers with consistent CSV output format.
"""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import time
import random


class BaseScraper(ABC):
    """
    Abstract base class for all grocery store scrapers.
    
    CSV Format:
    - store_name: Name of the store
    - product_name: Full product name
    - brand: Brand name (if available)
    - category: Main category
    - subcategory: Subcategory (if available)
    - price: Current price (numeric)
    - discounted_price: Discounted price if available (numeric or None)
    - unit: Unit of measurement (kg, g, L, ml, piece, etc.)
    - quantity: Quantity value (numeric)
    - url: Product URL
    - image_url: Product image URL
    - last_updated: Timestamp of scraping
    """
    
    def __init__(self, store_name: str, base_url: str, output_dir: str = "data"):
        """
        Initialize the base scraper.
        
        Args:
            store_name: Name of the store
            base_url: Base URL of the store website
            output_dir: Directory to save CSV files
        """
        self.store_name = store_name
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = self._setup_logger()
        
        # CSV headers
        self.csv_headers = [
            'store_name',
            'product_name',
            'brand',
            'category',
            'subcategory',
            'price',
            'discounted_price',
            'unit',
            'quantity',
            'url',
            'image_url',
            'last_updated'
        ]
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the scraper."""
        logger = logging.getLogger(f"{self.store_name}_scraper")
        logger.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        return logger
    
    def _rate_limit(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """
        Add random delay between requests to avoid overwhelming the server.
        
        Args:
            min_delay: Minimum delay in seconds
            max_delay: Maximum delay in seconds
        """
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _clean_price(self, price_str: str) -> Optional[float]:
        """
        Clean and convert price string to float.
        
        Args:
            price_str: Raw price string (e.g., "Rs. 1,234.56", "PKR 1234")
            
        Returns:
            Float price or None if parsing fails
        """
        if not price_str:
            return None
        
        try:
            # Remove common currency symbols and text
            cleaned = price_str.replace('Rs.', '').replace('PKR', '').replace('Rs', '')
            cleaned = cleaned.replace(',', '').strip()
            
            # Extract numeric value
            return float(cleaned)
        except (ValueError, AttributeError):
            self.logger.warning(f"Could not parse price: {price_str}")
            return None
    
    def _parse_unit_quantity(self, text: str) -> tuple[Optional[str], Optional[float]]:
        """
        Parse unit and quantity from product text.
        
        Args:
            text: Text containing unit info (e.g., "1kg", "500ml", "2L")
            
        Returns:
            Tuple of (unit, quantity)
        """
        if not text:
            return None, None
        
        import re
        
        # Common patterns
        patterns = [
            r'(\d+\.?\d*)\s*(kg|g|l|ml|piece|pcs|pack)',
            r'(\d+\.?\d*)(kg|g|l|ml|piece|pcs|pack)',
        ]
        
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                quantity = float(match.group(1))
                unit = match.group(2)
                return unit, quantity
        
        return None, None
    
    def save_to_csv(self, products: List[Dict], filename: Optional[str] = None):
        """
        Save scraped products to CSV file.
        
        Args:
            products: List of product dictionaries
            filename: Output filename (default: {store_name}_{timestamp}.csv)
        """
        if not products:
            self.logger.warning("No products to save")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.store_name.lower().replace(' ', '_')}_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_headers)
                writer.writeheader()
                
                for product in products:
                    # Ensure all required fields exist
                    row = {header: product.get(header, None) for header in self.csv_headers}
                    writer.writerow(row)
            
            self.logger.info(f"✓ Saved {len(products)} products to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving CSV: {e}")
    
    def validate_product(self, product: Dict) -> bool:
        """
        Validate that a product has minimum required fields.
        
        Args:
            product: Product dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['product_name', 'price']
        
        for field in required_fields:
            if not product.get(field):
                self.logger.warning(f"Product missing required field: {field}")
                return False
        
        return True
    
    @abstractmethod
    async def scrape(self) -> List[Dict]:
        """
        Main scraping method to be implemented by each store scraper.
        
        Returns:
            List of product dictionaries
        """
        pass
    
    @abstractmethod
    async def get_categories(self) -> List[Dict]:
        """
        Get all categories from the store.
        
        Returns:
            List of category dictionaries with name and URL
        """
        pass
    
    def create_product_dict(
        self,
        product_name: str,
        price: float,
        url: str,
        image_url: Optional[str] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        discounted_price: Optional[float] = None,
        unit: Optional[str] = None,
        quantity: Optional[float] = None
    ) -> Dict:
        """
        Create a standardized product dictionary.
        
        Args:
            product_name: Product name
            price: Current price
            url: Product URL
            image_url: Product image URL
            brand: Brand name
            category: Category name
            subcategory: Subcategory name
            discounted_price: Discounted price if available
            unit: Unit of measurement
            quantity: Quantity value
            
        Returns:
            Standardized product dictionary
        """
        return {
            'store_name': self.store_name,
            'product_name': product_name,
            'brand': brand,
            'category': category,
            'subcategory': subcategory,
            'price': price,
            'discounted_price': discounted_price,
            'unit': unit,
            'quantity': quantity,
            'url': url,
            'image_url': image_url,
            'last_updated': datetime.now().isoformat()
        }

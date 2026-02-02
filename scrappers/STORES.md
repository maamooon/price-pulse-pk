# Store URLs and Information

## Existing Stores (Scrapers in Jupyter Notebooks)

### 1. Metro
- **URL**: https://www.metro-online.pk
- **Status**: Scraper exists in `metro.ipynb`
- **Notes**: Uses Playwright for dynamic content

### 2. Jalalsons
- **URL**: https://jalalsons.com.pk
- **Status**: Scraper exists in `jalalsons.ipynb`
- **Notes**: Multi-branch support, uses Playwright

### 3. Rahim Store
- **URL**: (Need to verify from `rahim_store.ipynb`)
- **Status**: Scraper exists in `rahim_store.ipynb`
- **Notes**: To be converted to Python script

---

## New Stores (To Be Scraped)

### 4. Al-Fatah
- **URL**: https://alfatah.pk
- **Type**: Departmental store chain
- **Features**: 
  - Online grocery store
  - Home appliances, electronics, cosmetics
  - Cash on delivery available
  - Mobile app available
- **Coverage**: Pakistan-wide

### 5. Naheed
- **URL**: https://naheed.pk
- **Type**: Supermarket with e-commerce
- **Features**:
  - Groceries, makeup, skincare, electronics
  - Nationwide delivery
  - Mobile app available
  - Multiple categories (Grocery & Pet Care, Health & Beauty, etc.)
- **Coverage**: Pakistan-wide

### 6. Imtiaz
- **URL**: https://imtiaz.com.pk
- **Type**: Supermarket chain
- **Features**:
  - Mobile app for online ordering
  - Home delivery (selective areas)
  - Also available on foodpanda
- **Coverage**: Major cities (limited areas)
- **Notes**: May have limited online inventory

### 7. GreenValley
- **URL**: https://greenvalley.pk
- **Type**: Premium hypermarket
- **Features**:
  - Groceries, health & beauty, crockery
  - Imported goods available
  - Cash on delivery, online payments
- **Coverage**: Islamabad and Rawalpindi
- **Locations**: Lahore and Rawalpindi physical stores

### 8. GrocerApp
- **URL**: https://grocerapp.pk
- **Type**: Online grocery platform
- **Features**:
  - 5,000+ products
  - Same-day/next-day delivery
  - 300+ brands (Nestle, L'Oreal, etc.)
  - Multiple payment methods
  - 100% return policy
  - GrocerClub membership
- **Coverage**: Lahore, Islamabad, Rawalpindi, Faisalabad, Karachi

---

## Scraping Priority

1. **Phase 1**: Convert existing scrapers (Metro, Jalalsons, Rahim Store)
2. **Phase 2**: Create scrapers for stores with full online catalogs
   - GrocerApp (most comprehensive online platform)
   - Naheed (nationwide, good online presence)
   - Al-Fatah (large chain, good online catalog)
3. **Phase 3**: Create scrapers for limited coverage stores
   - GreenValley (limited to Islamabad/Rawalpindi)
   - Imtiaz (selective areas, may have limited online inventory)

---

## CSV Format (Consistent Across All Stores)

```csv
store_name,product_name,brand,category,subcategory,price,discounted_price,unit,quantity,url,image_url,last_updated
```

### Field Descriptions:
- **store_name**: Name of the store (e.g., "Metro", "Naheed")
- **product_name**: Full product name
- **brand**: Brand name (if available, else NULL)
- **category**: Main category (e.g., "Grocery", "Dairy")
- **subcategory**: Subcategory (if available, else NULL)
- **price**: Current/original price (numeric)
- **discounted_price**: Sale/discounted price (numeric or NULL)
- **unit**: Unit of measurement (kg, g, L, ml, piece, pack)
- **quantity**: Quantity value (numeric)
- **url**: Full product URL
- **image_url**: Product image URL
- **last_updated**: ISO 8601 timestamp

---

## Technical Notes

### Scraping Challenges:
1. **Dynamic Content**: Most sites use JavaScript rendering (need Playwright/Selenium)
2. **Rate Limiting**: Implement delays between requests
3. **Anti-Bot Measures**: May need to handle CAPTCHAs or IP blocking
4. **Data Consistency**: Different stores have different formats
5. **Missing Data**: Not all stores provide all fields (brand, discounts, etc.)

### Solutions:
- Use Playwright for all scrapers (consistent approach)
- Implement retry logic with exponential backoff
- Add user-agent rotation
- Respect robots.txt
- Cache responses to avoid re-scraping

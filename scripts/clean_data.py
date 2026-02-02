import pandas as pd
import re
import os
import glob
import numpy as np
from datetime import datetime

# Configuration
INPUT_DIR = r"d:\UNI\7th Semester\DS\Project\Smart-Price-Recommender\data"
OUTPUT_DIR = os.path.join(INPUT_DIR, "cleaned")

# Define canonical units
UNIT_MAP = {
    'g': 'g', 'gm': 'g', 'gram': 'g', 'gms': 'g', 'grams': 'g',
    'kg': 'kg', 'kilo': 'kg', 'kilogram': 'kg',
    'ml': 'ml', 'milliliter': 'ml',
    'l': 'l', 'litre': 'l', 'ltr': 'l', 'liter': 'l',
    'pcs': 'piece', 'piece': 'piece', 'packet': 'piece', 'pkt': 'piece', 'pack': 'piece', 'pc': 'piece'
}

# Regex for unit extraction from product name
# Look for patterns like "500g", "1.5 kg", "250ml", "1 Ltr", "4 Pcs"
UNIT_PATTERNS = [
    (r'(\d+(?:\.\d+)?)\s*(gm|g|gram|gms|grams|kg|kilogram|kilo|ml|milliliter|l|litre|ltr|liter|pcs|piece|pkt|pack|packet|pc)\b', 'full'),
]

def extract_units(name, current_unit, current_qty):
    """Try to extract unit and quantity from name if they are missing or inconsistent."""
    if pd.notna(current_unit) and pd.notna(current_qty) and current_unit != '' and current_qty != 0:
        # Standardize existing unit
        standard_unit = UNIT_MAP.get(str(current_unit).lower(), str(current_unit).lower())
        return standard_unit, float(current_qty)
    
    # Try regex extraction
    match = re.search(r'(\d+(?:\.\d+)?)\s*(gm|g|gram|gms|grams|kg|kilogram|kilo|ml|milliliter|l|litre|ltr|liter|pcs|piece|pkt|pack|packet|pc)\b', str(name), re.IGNORECASE)
    if match:
        qty = float(match.group(1))
        unit_raw = match.group(2).lower()
        unit = UNIT_MAP.get(unit_raw, unit_raw)
        return unit, qty
    
    return current_unit, current_qty

def clean_jalalsons(df):
    print("Cleaning Jalalsons specific patterns...")
    # Remove branch names like [Allama Iqbal Town Branch Lahore]
    df['product_name'] = df['product_name'].str.replace(r'\[.*?\]', '', regex=True).str.strip()
    return df

def clean_metro(df):
    print("Cleaning Metro specific patterns...")
    # Normalize generic category
    df.loc[df['category'] == 'Metro Post Grocery', 'category'] = ''
    return df

def clean_rahim_store(df):
    print("Cleaning Rahim Store specific patterns...")
    # Department 001 is useless
    df.loc[df['category'] == 'Department 001', 'category'] = ''
    return df

def standardize_dataset(df):
    print("Applying global standardization...")
    
    # 1. Basic Cleaning
    df['product_name'] = df['product_name'].fillna('').str.strip()
    df['brand'] = df['brand'].fillna('').str.strip()
    df['category'] = df['category'].fillna('').str.strip()
    df['subcategory'] = df['subcategory'].fillna('').str.strip()
    
    # 2. Extract Units/Quantity
    df[['unit', 'quantity']] = df.apply(
        lambda x: pd.Series(extract_units(x['product_name'], x['unit'], x['quantity'])), 
        axis=1
    )
    
    # 3. Numeric Prices
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['discounted_price'] = pd.to_numeric(df['discounted_price'], errors='coerce')
    
    # 4. Brand Extraction (if missing, take first word of product name)
    # This is a heuristic, can be improved
def infer_brand(row):
    name = str(row['product_name'])
    brand = str(row['brand'])
    
    # If brand is generic or missing, try to extract from name
    if brand == '' or any(x in brand.lower() for x in ['alfatah', 'greenvalley', 'rahim', 'metro', 'jalalsons']):
        # Expanded list of common brands
        common_brands = [
            'National', 'Shan', 'Youngs', 'Nestle', 'Olpers', 'Milkpak', 'Tapal', 'Rafhan', 'Mezan', 'Shezan',
            'Bread & Beyond', 'Almarai', 'Blue Band', 'Knorr', 'Maggi', 'Lipton', 'Dawn', 'Mitchells',
            'LU', 'Peak Freans', 'EBM', 'Coca Cola', 'Pepsi', 'Aquafina', 'Nestle Pure Life', 'Sprite', '7Up', 'Fanta',
            'Surf Excel', 'Ariel', 'Lux', 'Dove', 'Sunlight', 'Vim', 'Dettol', 'Lifebuoy', 'Panteen', 'Sunsilk',
            'Colgate', 'Sensodyne', 'Pepsodent', 'Palmolive', 'Head & Shoulders', 'Safeguard', 'Gillette',
            'Loreal', 'Garnier', 'Nivea', 'Fair & Lovely', 'Ponds', 'Johnson', 'Huggies', 'Pampers', 'Molfix',
            'Dalda', 'Habib', 'Sufi', 'Tullo', 'Kashmir', 'Canolive', 'Soya Supreme',
            'Nurpur', 'Dayfresh', 'Adams', 'Puck', 'Kiri', 'Happy Cow', 'Kraft', 'Anchor',
            'Kolson', 'Indomie', 'Slanty', 'Lays', 'Kurkure', 'Cheetos', 'Pringles'
        ]
        
        for b in common_brands:
            if name.lower().startswith(b.lower()):
                return b
        
        # secondary check: is brand in the name at all?
        for b in common_brands:
            if f" {b.lower()} " in f" {name.lower()} ":
                return b

        # fallback: first word if not numeric and > 2 chars
        first_word = name.split()[0] if name.split() else ''
        if first_word and not any(char.isdigit() for char in first_word) and len(first_word) > 2:
            return first_word

    return brand

def map_category(row):
    name = str(row['product_name']).lower()
    cat = str(row['category']).lower()
    subcat = str(row['subcategory']).lower()
    text = f"{name} {cat} {subcat}"
    
    mapping = {
        'Bakery': ['bread', 'bun', 'pita', 'rusk', 'cake', 'pastry', 'bakery', 'croissant', 'muffin', 'sheermal', 'naan'],
        'Fruits & Vegetables': ['fruit', 'vegetable', 'tomato', 'potato', 'onion', 'apple', 'banana', 'orange', 'mango', 'citrus', 'berry', 'leafy', 'root', 'gourd'],
        'Meat & Seafood': ['chicken', 'beef', 'mutton', 'fish', 'seafood', 'mince', 'frankfurter', 'nugget', 'sausage', 'kebab', 'meat', 'prawn', 'steak'],
        'Beverages': ['juice', 'soft drink', 'tea', 'coffee', 'water', 'coke', 'pepsi', 'milkpak', 'drink', 'beverage', 'squash', 'syrup', 'energy drink', 'soda'],
        'Pantry Essentials': ['oil', 'ghee', 'spice', 'masala', 'salt', 'sugar', 'pulse', 'daal', 'flour', 'atta', 'ketchup', 'sauce', 'mayo', 'jam', 'honey', 'vinegar', 'pickle', 'lentil', 'rice', 'pasta', 'noodle', 'vermicelli'],
        'Dairy & Eggs': ['milk', 'egg', 'cheese', 'butter', 'cream', 'yogurt', 'margarine', 'dairy', 'whitener', 'khoya', 'paneer'],
        'Snacks & Sweets': ['chip', 'biscuit', 'snack', 'candy', 'chocolate', 'nimko', 'popcorn', 'jelly', 'custard', 'dessert', 'cookie', 'wafer', 'crackers', 'marshmallow'],
        'Household & Personal Care': ['soap', 'shampoo', 'detergent', 'cleaning', 'mop', 'tissue', 'diaper', 'care', 'handwash', 'toothpaste', 'brush', 'laundry', 'deodorant', 'lotion', 'cream', 'face wash', 'shaving', 'sanitary', 'insecticide', 'freshener']
    }
    
    # Priority mapping for generic categories
    if cat in ['general', 'grocery', 'grocery foods', 'daily essentials', 'food & beverages', 'department 002', 'department 004', 'metro post grocery', 'grocery non food', '']:
        for target_cat, keywords in mapping.items():
            if any(kw in text for kw in keywords):
                return target_cat
            
    return row['category'] if row['category'] != '' else 'Other'

def standardize_dataset(df):
    print("Applying global standardization...")
    
    # 1. Basic Cleaning
    df['product_name'] = df['product_name'].fillna('').str.strip()
    df['brand'] = df['brand'].fillna('').str.strip()
    df['category'] = df['category'].fillna('').str.strip()
    df['subcategory'] = df['subcategory'].fillna('').str.strip()
    
    # 2. Extract Units/Quantity
    df[['unit', 'quantity']] = df.apply(
        lambda x: pd.Series(extract_units(x['product_name'], x['unit'], x['quantity'])), 
        axis=1
    )
    
    # 3. Numeric Prices
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['discounted_price'] = pd.to_numeric(df['discounted_price'], errors='coerce')
    
    # 4. Brand Extraction/Inference
    df['brand'] = df.apply(infer_brand, axis=1)
    
    # 5. Category Normalization
    df['category'] = df.apply(map_category, axis=1)
    
    # 6. Weight Standardization (for ML/Comparison)
    def standardize_weight(unit, qty):
        if pd.isna(qty) or qty == 0: return np.nan
        unit = str(unit).lower()
        if unit == 'kg': return qty * 1000
        if unit == 'l': return qty * 1000
        if unit in ['g', 'ml']: return qty
        return np.nan

    df['standardized_weight_g_ml'] = df.apply(lambda x: standardize_weight(x['unit'], x['quantity']), axis=1)
    
    # 6. Deduplication
    initial_count = len(df)
    df = df.drop_duplicates(subset=['store_name', 'product_name', 'unit', 'quantity'], keep='first')
    print(f"Removed {initial_count - len(df)} duplicates.")
    
    return df

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    csv_files = glob.glob(os.path.join(INPUT_DIR, "*.csv"))
    
    all_data = []

    for file in csv_files:
        filename = os.path.basename(file)
        print(f"\nProcessing {filename}...")
        
        df = pd.read_csv(file)
        
        # Store specific cleaning
        if 'jalalsons' in filename.lower():
            df = clean_jalalsons(df)
        elif 'metro' in filename.lower():
            df = clean_metro(df)
        elif 'rahim_store' in filename.lower():
            df = clean_rahim_store(df)
        
        # Global standardization
        df = standardize_dataset(df)
        
        # Save individual cleaned file
        output_file = os.path.join(OUTPUT_DIR, f"cleaned_{filename}")
        df.to_csv(output_file, index=False)
        print(f"Saved cleaned file to {output_file}")
        
        all_data.append(df)

    # Combine all data for global validation
    if all_data:
        merged_df = pd.concat(all_data, ignore_index=True)
        merged_output = os.path.join(OUTPUT_DIR, "merged_cleaned_data.csv")
        merged_df.to_csv(merged_output, index=False)
        print(f"\nMerged all data into {merged_output}")
        print(f"Total products: {len(merged_df)}")

if __name__ == "__main__":
    main()

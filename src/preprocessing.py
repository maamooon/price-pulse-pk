import re
import string

def normalize_text(text: str) -> str:
    """
    Standardize text by lowercasing, removing punctuation, and stripping whitespace.
    """
    if not isinstance(text, str):
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_unit_qty(text: str):
    """
    Extract numeric value and unit from strings like '250ml', '1.5 Litre', '500 g'.
    Returns (value: float, unit: str)
    """
    if not text:
        return 0.0, ""
    
    text = text.lower().replace(" ", "")
    # Find numbers (integers or decimals)
    qty_match = re.search(r'(\d+\.?\d*)', text)
    qty = float(qty_match.group(1)) if qty_match else 0.0
    
    # Find common units
    unit = ""
    if any(u in text for u in ['ml', 'millilitre']): unit = "ml"
    elif any(u in text for u in ['litre', 'ltr', 'l']): unit = "l"
    elif any(u in text for u in ['gram', 'gm', 'g']): unit = "g"
    elif any(u in text for u in ['kg', 'kilogram']): unit = "kg"
    elif 'pc' in text or 'piece' in text: unit = "pcs"
    
    return qty, unit

def clean_product_name(name: str) -> str:
    name = normalize_text(name)
    # Remove common irrelevant words for better fuzzy matching
    name = re.sub(r'\b(full cream|milk|product|new|pack|original)\b', '', name)
    return name

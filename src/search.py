import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .preprocessing import normalize_text, extract_unit_qty, clean_product_name

class SearchEngine:
    def __init__(self):
        """Initialize the search engine with TF-IDF vectorizer."""
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        self.products_df = None
        self.tfidf_matrix = None
        self.refresh_index()
    
    def refresh_index(self):
        """Load products from DB and fit TF-IDF vectorizer."""
        from .database import SessionLocal
        from .models import Product, Store
        
        db = SessionLocal()
        try:
            # Join with Store to get store name
            query = db.query(Product, Store.name.label("store_name")).join(Store)
            self.products_df = pd.read_sql(query.statement, db.get_bind())
            
            if self.products_df.empty:
                print("Search index is empty. Please run ingestion first.")
                return

            # Combine name and brand for search context
            self.products_df['search_text'] = self.products_df['name'].fillna('') + " " + self.products_df['brand'].fillna('')
            self.products_df['search_text'] = self.products_df['search_text'].apply(normalize_text)
            
            self.tfidf_matrix = self.vectorizer.fit_transform(self.products_df['search_text'])
            print(f"Search index built with {self.products_df.shape[0]} products.")
        finally:
            db.close()

    def search(self, query: str, top_n: int = 20):
        print(f"DEBUG: Searching for '{query}'")
        if self.tfidf_matrix is None:
            print("DEBUG: TF-IDF Matrix is None")
            return []

        query_norm = normalize_text(query)
        print(f"DEBUG: Normalized query: '{query_norm}'")
        
        try:
            query_vec = self.vectorizer.transform([query_norm])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            
            # Get top indices
            top_indices = similarities.argsort()[-top_n:][::-1]
            
            results = []
            final_groups = []
            
            # Extract candidates that have some similarity
            candidates = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score > 0:
                    candidates.append({
                        "row": self.products_df.iloc[idx],
                        "score": score
                    })

            for cand in candidates:
                row = cand["row"]
                score = cand["score"]
                
                # Robust extraction of Unit and Qty
                # Look into 'unit' column first, fallback to 'name' if empty
                raw_unit_str = f"{row['quantity']} {row['unit']}" if pd.notna(row['unit']) else str(row['name'])
                qty, unit = extract_unit_qty(raw_unit_str)
                
                name_raw = str(row['name']).split('[')[0].strip()
                brand = str(row['brand']).lower() if pd.notna(row['brand']) else ""
                
                # Descriptive-cleaned name for token matching
                name_trimmed = clean_product_name(name_raw)
                tokens = set(name_trimmed.split())
                
                price = float(row['price']) if pd.notna(row['price']) else 0.0
                
                store_info = {
                    "store_name": row['store_name'],
                    "price": price,
                    "url": row['url'],
                    "discounted_price": float(row['discounted_price']) if pd.notna(row['discounted_price']) else None
                }
                
                found_group = False
                for group in final_groups:
                    # 1. Compare Units and Qty (Crucial)
                    if group['unit'] == unit and abs(group['qty'] - qty) < 0.001:
                        # 2. Compare Brand
                        if brand == group['brand'] and brand != "":
                            # Exact brand match + same unit = Highly likely same product
                            # Even if name differs slightly (e.g. 'Milkpak' vs 'Milkpak Full Cream')
                            common = tokens.intersection(group['tokens'])
                            if len(common) > 0: # At least one core word in common
                                # Handle branch duplicates: only keep the lowest price per store
                                existing = next((s for s in group['all_prices'] if s['store_name'] == store_info['store_name']), None)
                                if existing:
                                    if store_info['price'] < existing['price']:
                                        existing.update(store_info)
                                else:
                                    group['all_prices'].append(store_info)
                                    
                                group['min_price'] = min(group['min_price'], price)
                                if score > group['similarity_score']:
                                    group['similarity_score'] = score
                                found_group = True
                                break
                        
                        # 3. No brand match / generic: Check price window and high token overlap
                        if group['min_price'] > 0 and (0.6 <= (price / group['min_price']) <= 1.6):
                            overlap = len(tokens.intersection(group['tokens'])) / max(len(tokens), len(group['tokens']))
                            if overlap > 0.6:
                                # Handle branch duplicates
                                existing = next((s for s in group['all_prices'] if s['store_name'] == store_info['store_name']), None)
                                if existing:
                                    if store_info['price'] < existing['price']:
                                        existing.update(store_info)
                                else:
                                    group['all_prices'].append(store_info)

                                group['min_price'] = min(group['min_price'], price)
                                if score > group['similarity_score']:
                                    group['similarity_score'] = score
                                found_group = True
                                break
                
                if not found_group:
                    product = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
                    product['name'] = name_raw
                    product['similarity_score'] = score
                    product['all_prices'] = [store_info]
                    
                    final_groups.append({
                        **product,
                        "tokens": tokens,
                        "brand": brand,
                        "unit": unit,
                        "qty": qty,
                        "min_price": price
                    })
            
            # Sort prices within each group and clean up metadata
            for g in final_groups:
                g['all_prices'] = sorted(g['all_prices'], key=lambda x: x['price'])
                for key in ['tokens', 'min_price', 'qty']:
                    g.pop(key, None)

            print(f"DEBUG: Found {len(final_groups)} fuzzy grouped matches (from {len(candidates)} candidates)")
            return final_groups
        except Exception as e:
            print(f"DEBUG: Error in search: {e}")
            import traceback
            traceback.print_exc()
            return []

    def search_by_id(self, product_id: int):
        if self.products_df is None:
            return None
        match = self.products_df[self.products_df['id'] == product_id]
        if match.empty:
            return None
        
        # Convert to dict and replace NaN with None
        row = match.iloc[0]
        return {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}

# Singleton instance
search_engine = SearchEngine()

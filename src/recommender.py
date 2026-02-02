from .search import search_engine
from .preprocessing import normalize_text, extract_unit_qty
import pandas as pd
import numpy as np

class Recommender:
    def __init__(self, search_engine_instance):
        self.search_engine = search_engine_instance

    def recommend(self, product_id: int, top_n: int = 6):
        df = self.search_engine.products_df
        if df is None or product_id not in df['id'].values:
            return []

        target_row = df[df['id'] == product_id].iloc[0]
        target_name = str(target_row['name'])
        target_brand = str(target_row['brand']).lower() if pd.notna(target_row['brand']) else ""
        target_cat = str(target_row['category']).lower() if pd.notna(target_row['category']) else ""
        target_price = float(target_row['price'])
        target_qty, target_unit = extract_unit_qty(target_name)

        # 1. Broad candidate search (use category and brand as tokens)
        search_query = f"{target_brand} {target_cat} {target_name}".strip()
        candidates = self.search_engine.search(search_query, top_n=50)
        
        scored_candidates = []
        seen_names = set([target_name.lower()]) # Avoid suggesting the same product variants

        for cand in candidates:
            # Skip the target product group
            if cand['id'] == product_id:
                continue
            
            cand_name = str(cand['name']).lower()
            if cand_name in seen_names:
                continue
            
            cand_brand = str(cand['brand']).lower() if cand['brand'] else ""
            cand_cat = str(cand['category']).lower() if cand['category'] else ""
            cand_price = float(cand['price'])
            
            # Weighted Scoring
            score = 0
            reasons = []
            
            # A. Brand Match (Strong signal)
            if target_brand and cand_brand == target_brand:
                score += 0.4
                reasons.append(f"More from {cand['brand']}")
            
            # B. Category Match
            if target_cat and cand_cat == target_cat:
                score += 0.3
                reasons.append("Same category")
            
            # C. TF-IDF Similarity (already in cand['similarity_score'])
            score += (cand.get('similarity_score', 0) * 0.3)
            
            # D. Price Context
            price_ratio = cand_price / target_price if target_price > 0 else 1
            if 0.8 <= price_ratio <= 1.2:
                reasons.append("Similar price")
            elif price_ratio < 0.8:
                reasons.append("Better value option")
            elif price_ratio > 1.5:
                # Penalty for being way too expensive for a 'recommendation' 
                # unless it's a premium brand match
                if cand_brand != target_brand:
                    score -= 0.2
            
            # E. Diversity Check: Don't suggest 10 types of milk if we already have 2
            # (Simple: just add to seen names)
            seen_names.add(cand_name)
            
            if score > 0.2: # Minimum threshold
                cand['final_rec_score'] = score
                cand['recommendation_reasons'] = " | ".join(reasons[:2]) # Keep top 2 reasons
                scored_candidates.append(cand)

        # Sort by final score
        scored_candidates = sorted(scored_candidates, key=lambda x: x['final_rec_score'], reverse=True)
        
        return scored_candidates[:top_n]

recommender = Recommender(search_engine)

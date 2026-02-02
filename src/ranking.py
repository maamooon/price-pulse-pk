import numpy as np

class Ranker:
    def rank_results(self, results):
        if not results:
            return []

        # Convert list of dicts to a local list for processing
        ranked_list = []
        
        # Calculate max/min price for normalization
        prices = [r['price'] for r in results if r['price'] > 0]
        if not prices:
            return results
            
        max_price = max(prices)
        min_price = min(prices)
        price_range = max_price - min_price if max_price != min_price else 1.0

        for res in results:
            # 1. Similarity Score (0.5 weight)
            sim_score = res.get('similarity_score', 0)
            
            # 2. Price Score (0.3 weight) 
            # Lower price is better -> Score = 1 - normalized_price
            normalized_price = (res['price'] - min_price) / price_range
            price_score = 1.0 - normalized_price
            
            # 3. Brand/Availability Score (0.2 weight)
            # For now, let's just use 1 if brand exists, 0 otherwise
            brand_score = 1.0 if res.get('brand') else 0.5
            
            # Final Weighted Sum
            final_score = (sim_score * 0.5) + (price_score * 0.3) + (brand_score * 0.2)
            
            res['final_ranking_score'] = float(final_score)
            ranked_list.append(res)
            
        # Re-sort results by final score
        return sorted(ranked_list, key=lambda x: x['final_ranking_score'], reverse=True)

ranker = Ranker()

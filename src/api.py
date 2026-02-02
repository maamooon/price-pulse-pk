from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from .search import search_engine
from .recommender import recommender
from .ranking import ranker
from .database import SessionLocal
from .models import Product, Store

app = FastAPI(title="Smart Price Recommender API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caching for search queries (Simple in-memory cache)
query_cache = {}

class StorePrice(BaseModel):
    store_name: str
    price: float
    url: str
    discounted_price: Optional[float] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    brand: Optional[str]
    category: Optional[str]
    price: float
    discounted_price: Optional[float]
    unit: Optional[str]
    quantity: Optional[float]
    store_name: str
    url: str
    image_url: Optional[str]
    similarity_score: Optional[float] = None
    final_ranking_score: Optional[float] = None
    recommendation_reasons: Optional[str] = None
    all_prices: Optional[List[StorePrice]] = None

@app.get("/")
def health_check():
    return {"status": "up", "database": "connected"}

@app.get("/search", response_model=List[ProductResponse])
def search_products(query: str = Query(..., min_length=1)):
    try:
        # Check cache
        if query in query_cache:
            return query_cache[query]
        
        results = search_engine.search(query)
        if not results:
            return []
        
        # Apply ranking
        ranked_results = ranker.rank_results(results)
        
        # Limit cache size
        if len(query_cache) > 100:
            query_cache.pop(next(iter(query_cache)))
            
        query_cache[query] = ranked_results
        return ranked_results
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/compare/{product_id}")
def compare_prices(product_id: int):
    results = search_engine.search_by_id(product_id) # Need to implement this helper
    if not results:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Logic to find same product in other stores
    # (Simplified: search for the exact product name in the engine)
    matches = search_engine.search(results['name'], top_n=50)
    
    comparison = {
        "target": results,
        "alternatives": [m for m in matches if m['id'] != product_id]
    }
    
    # Highlight cheapest
    all_prices = [m['price'] for m in matches]
    comparison['min_price'] = min(all_prices) if all_prices else results['price']
    comparison['max_price'] = max(all_prices) if all_prices else results['price']
    
    return comparison

@app.get("/product/{product_id}", response_model=ProductResponse)
def get_product_details(product_id: int):
    # Get the raw product
    raw_product = search_engine.search_by_id(product_id)
    if not raw_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # To get the grouped version (all prices), we can search for the product name
    # The fuzzy grouping in .search() will consolidate it
    results = search_engine.search(raw_product['name'], top_n=10)
    for res in results:
        if res['id'] == product_id:
            return res
            
    # Fallback to the raw product if grouping didn't catch it for some reason
    return raw_product

@app.get("/recommend/{product_id}", response_model=List[ProductResponse])
def get_recommendations(product_id: int):
    recs = recommender.recommend(product_id)
    if not recs:
        return []
    return recs

@app.get("/stores")
def get_stores():
    db = SessionLocal()
    try:
        return db.query(Store).all()
    finally:
        db.close()

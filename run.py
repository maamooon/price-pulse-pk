import uvicorn
import os
from src.data_loader import init_db

if __name__ == "__main__":
    # Initialize database tables
    init_db()
    
    # Test search manually to debug
    print("--- MANUAL SEARCH TEST ---")
    from src.search import search_engine
    results = search_engine.search("milk")
    print(f"Manual Search Results: {len(results)}")
    print("--------------------------")
    
    # Start the server
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)

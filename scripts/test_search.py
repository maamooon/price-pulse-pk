import sys
import os

# Ensure we can find src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.search import search_engine

print("--- STANDALONE SEARCH TEST ---")
try:
    search_engine.refresh_index()
    results = search_engine.search("milk", top_n=5)
    print(f"Results found: {len(results)}")
    for r in results:
        print(f"- {r['name']} ({r['store_name']}) - Score: {r['similarity_score']}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
print("------------------------------")

import sys
sys.path.insert(0, '.')

from src.search import search_engine
from src.ranking import ranker

print("Testing Search Engine and Ranker")
print("=" * 50)

# Test 1: Check if search engine is initialized
print("\n1. Search Engine Status:")
print(f"   Products DF exists: {search_engine.products_df is not None}")
print(f"   TF-IDF Matrix exists: {search_engine.tfidf_matrix is not None}")

if search_engine.products_df is not None:
    print(f"   Number of products: {len(search_engine.products_df)}")

# Test 2: Try a search
print("\n2. Testing Search:")
try:
    results = search_engine.search('milk', top_n=3)
    print(f"   ✓ Search successful")
    print(f"   Results found: {len(results)}")
    
    if results:
        print(f"\n   First result:")
        first = results[0]
        print(f"     Name: {first.get('name', 'N/A')}")
        print(f"     Price: {first.get('price', 'N/A')}")
        print(f"     Store: {first.get('store_name', 'N/A')}")
        print(f"     Similarity: {first.get('similarity_score', 'N/A')}")
        print(f"     Keys: {list(first.keys())}")
except Exception as e:
    print(f"   ✗ Search failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Try ranking
print("\n3. Testing Ranker:")
try:
    if results:
        ranked = ranker.rank_results(results)
        print(f"   ✓ Ranking successful")
        print(f"   Ranked results: {len(ranked)}")
        
        if ranked:
            print(f"\n   Top result after ranking:")
            top = ranked[0]
            print(f"     Name: {top.get('name', 'N/A')}")
            print(f"     Final score: {top.get('final_ranking_score', 'N/A')}")
except Exception as e:
    print(f"   ✗ Ranking failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)

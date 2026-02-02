import pandas as pd
import os
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .models import Store, Product

def init_db():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

def load_data_to_db(csv_path: str):
    if not os.path.exists(csv_path):
        print(f"Error: File {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    db = SessionLocal()
    
    try:
        # 1. Handle Stores
        unique_stores = df['store_name'].unique()
        store_map = {}
        for store_name in unique_stores:
            store = db.query(Store).filter(Store.name == store_name).first()
            if not store:
                store = Store(name=store_name)
                db.add(store)
                db.commit()
                db.refresh(store)
            store_map[store_name] = store.id
        
        print(f"Associated {len(store_map)} stores.")

        # 2. Handle Products (Batch insert)
        products_to_add = []
        for _, row in df.iterrows():
            product = Product(
                name=row['product_name'],
                brand=row.get('brand'),
                category=row.get('category'),
                subcategory=row.get('subcategory'),
                price=row['price'],
                discounted_price=row.get('discounted_price'),
                unit=row.get('unit'),
                quantity=row.get('quantity'),
                standardized_weight=row.get('standardized_weight_g_ml'),
                url=row['url'],
                image_url=row.get('image_url'),
                store_id=store_map[row['store_name']]
            )
            products_to_add.append(product)
            
            # Batch commit every 1000 items
            if len(products_to_add) >= 1000:
                db.bulk_save_objects(products_to_add)
                db.commit()
                products_to_add = []
        
        if products_to_add:
            db.bulk_save_objects(products_to_add)
            db.commit()
            
        print(f"Successfully ingested {len(df)} products into the database.")
        
    except Exception as e:
        print(f"An error occurred during ingestion: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # This part allows running the script standalone from the root directory
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    init_db()
    CSV_PATH = r"data\cleaned\merged_cleaned_data.csv"
    load_data_to_db(CSV_PATH)

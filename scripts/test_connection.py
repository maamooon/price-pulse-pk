import os
import urllib.parse
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

raw_url = os.getenv("DATABASE_URL")

# Explicitly encode the password part
# postgresql://user:pass@host/db
try:
    prefix, rest = raw_url.split("://")
    auth, host_db = rest.split("@")
    user, password = auth.split(":", 1)
    
    encoded_password = urllib.parse.quote_plus(password)
    DATABASE_URL = f"{prefix}://{user}:{encoded_password}@{host_db}"
    
    print(f"Testing connection to (encoded): {host_db}")
    
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Success: Database is reachable!")
except Exception as e:
    print(f"Error connecting to the database: {e}")

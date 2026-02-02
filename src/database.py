import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Default to local postgres if not specified
raw_url = os.getenv("DATABASE_URL")

if raw_url and "://" in raw_url and "@" in raw_url:
    try:
        # Handle password encoding for special characters like &, ?, %
        prefix, rest = raw_url.split("://", 1)
        auth, host_db = rest.split("@", 1)
        if ":" in auth:
            user, password = auth.split(":", 1)
            # Always encode the password to handle special chars like &, ?, %
            password = urllib.parse.quote_plus(password)
            DATABASE_URL = f"{prefix}://{user}:{password}@{host_db}"
        else:
            DATABASE_URL = raw_url
    except Exception:
        DATABASE_URL = raw_url
else:
    DATABASE_URL = raw_url

print(f"Connecting to: {DATABASE_URL.split('@')[-1] if '@' in str(DATABASE_URL) else 'Unknown'}")

# Supabase requires SSL
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

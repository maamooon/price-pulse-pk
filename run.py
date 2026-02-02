import uvicorn
from src.data_loader import init_db

if __name__ == "__main__":
    # Initialize database tables
    init_db()
    
    # Start the server
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)

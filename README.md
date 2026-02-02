# Smart Price Recommender

A production-ready, entry-level friendly product price comparison and recommendation system built with **FastAPI**, **PostgreSQL**, and **React**.

## 🚀 Features
- **TF-IDF Search**: Fast and relevant product search across multiple stores.
- **Explainable Recommendations**: Content-based suggestions with clear justifications.
- **Price Comparison**: High-level comparison across different stores for the same item.
- **Weighted Ranking**: Results ranked by a combination of similarity, price, and brand status.

## 🛠️ Technology Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **ML**: Scikit-Learn (TF-IDF Vectorization)
- **Frontend**: React (Vite)

## 📦 Local Setup

### 1. Database
Install PostgreSQL locally and create a database named `smart_price_db`.

### 2. Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your local DB credentials
```

### 3. Data Ingestion
Run the runner script to initialize the DB and load the cleaned CSV data:
```bash
python run.py
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🌐 Online Deployment (PostgreSQL Online)

The PostgreSQL setup I've provided is **cloud-ready**. You can use an "Online PostgreSQL" service to host your data on the web.

### 1. Recommended Services
- **[Supabase](https://supabase.com)** (Free tier available)
- **[Neon.tech](https://neon.tech)** (Serverless Postgres, very easy setup)
- **[Render](https://render.com)** (Managed Postgres)

### 2. Procedure to use Online DB
1. **Sign Up**: Create an account on any service above (e.g., Neon.tech).
2. **Create Database**: Click "Create New Project" -> Name it `smart_price_db`.
3. **Get Connection String**: The service will provide a URL similar to:
   `postgresql://owner:pass@ep-cool-flower-123.us-east-2.aws.neon.tech/smart_price_db`
4. **Update .env**: Replace your local `DATABASE_URL` with this online URL.
5. **Run Ingestion**: Run `python run.py` again. It will now connect to the cloud and upload your data to the online server.

---

## 🧠 ML & Recommendation Logic

### Why TF-IDF?
We chose **TF-IDF (Term Frequency-Inverse Document Frequency)** because it is highly interpretable. It assigns weights to words based on how unique they are to a product. For example, "Milk" is common, but "Olpers" or "Full Cream" are more unique and help in better matching.

### Ranking Formula
Results are ranked using a **Weighted Score**:
- **50% Text Similarity**: How well the name matches the query.
- **30% Price Score**: Normalized price rank (lower prices get higher scores).
- **20% Brand Relevance**: Presence of a recognized brand name.

### Explainability
Recommendations aren't a "black box". The system checks for specific overlap in categories, brands, and price brackets to generate reasons like *"Same brand"* or *"Lower price option"*.

## 📝 Assumptions & Limitations
- **Content-Based Only**: Does not track user history (privacy-focused).
- **Static Scrapes**: Relies on the latest CSV data provided during ingestion.
- **Exact Match for Comparisons**: Currently uses fuzzy name matching to group similar items across stores.

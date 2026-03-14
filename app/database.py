"""
database.py
-----------
Handles:
  - Loading the .env file for credentials
  - Connecting to MongoDB Atlas
  - Cleaning and inserting the Netflix CSV (only once)
  - Fetching and filtering data for the dashboard
"""

import os
import pandas as pd
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import streamlit as st
import certifi

# ---------------------------------------------------------------------------
# Load environment variables from .env file
# When running locally:  reads from the .env file in your project root
# When running in Docker: reads from environment variables set in docker-compose
# ---------------------------------------------------------------------------
from dotenv import load_dotenv
load_dotenv()

MONGO_URI        = os.environ.get("MONGO_URI",        "mongodb://localhost:27017")
MONGO_DB         = os.environ.get("MONGO_DB",         "netflix_db")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "titles")

# Path to the CSV — works both locally and inside Docker
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "netflix_titles.csv")


# ---------------------------------------------------------------------------
# MongoDB client
# @st.cache_resource creates the connection once and reuses it across reruns.
# Without this, Streamlit would reconnect to Atlas on every interaction.
# ---------------------------------------------------------------------------
@st.cache_resource
def get_mongo_client():
    """
    Connect to MongoDB Atlas.
    Atlas connections use the mongodb+srv:// protocol which handles
    automatic failover and load balancing across Atlas nodes.
    """
    try:
        client = MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=10000,  # 10 seconds — Atlas can be slightly slower than local
            tls=True,                        # Atlas always requires TLS/SSL
        )
        # Actually test the connection — ping returns immediately if connected
        client.admin.command("ping")
        return client
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise Exception(
            f"Cannot connect to MongoDB Atlas.\n\n"
            f"Check that:\n"
            f"  1. Your MONGO_URI in .env is correct\n"
            f"  2. Your IP address is whitelisted in Atlas Network Access\n"
            f"  3. Your database username and password are correct\n\n"
            f"Original error: {e}"
        )


def get_collection():
    """Return the Netflix titles collection."""
    client = get_mongo_client()
    db = client[MONGO_DB]
    return db[MONGO_COLLECTION]


# ---------------------------------------------------------------------------
# Data cleaning
# ---------------------------------------------------------------------------
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize the raw Netflix CSV."""
    df = df.copy()

    # Fill missing text fields with sensible defaults
    df["director"]    = df["director"].fillna("Unknown")
    df["cast"]        = df["cast"].fillna("Unknown")
    df["country"]     = df["country"].fillna("Unknown")
    df["rating"]      = df["rating"].fillna("Not Rated")
    df["duration"]    = df["duration"].fillna("Unknown")
    df["listed_in"]   = df["listed_in"].fillna("Unknown")
    df["description"] = df["description"].fillna("")

    # Parse date_added into a proper datetime object
    df["date_added"]  = pd.to_datetime(df["date_added"].str.strip(), errors="coerce")
    df["year_added"]  = df["date_added"].dt.year
    df["month_added"] = df["date_added"].dt.month

    # Pull the number out of duration strings like "90 min" or "3 Seasons"
    df["duration_int"] = df["duration"].str.extract(r"(\d+)").astype(float)

    # Clean up type and release year
    df["type"]         = df["type"].str.strip()
    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")

    return df


# ---------------------------------------------------------------------------
# Load data into Atlas
# ---------------------------------------------------------------------------
def load_data_to_mongo():
    """
    Read netflix_titles.csv, clean it, and insert into Atlas.
    Checks if data already exists first — so this is safe to call
    on every app startup without duplicating data.
    """
    collection = get_collection()

    # If documents already exist, skip — prevents duplicating data on restart
    if collection.count_documents({}) > 0:
        return

    df = pd.read_csv(DATA_PATH)
    df = clean_dataframe(df)

    # MongoDB cannot store pandas NaT or NaN — replace with Python None
    df = df.where(pd.notnull(df), None)

    # Convert datetime objects to ISO string for storage
    df["date_added"] = df["date_added"].apply(
        lambda x: x.isoformat() if x is not None else None
    )

    # Convert rows to dicts and bulk insert
    records = df.to_dict(orient="records")
    collection.insert_many(records)

    # Indexes make filter queries significantly faster
    collection.create_index([("type",         ASCENDING)])
    collection.create_index([("release_year", ASCENDING)])
    collection.create_index([("year_added",   ASCENDING)])
    collection.create_index([("country",      ASCENDING)])


# ---------------------------------------------------------------------------
# Fetch data from Atlas
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)
def fetch_all_data() -> pd.DataFrame:
    """
    Pull every document from Atlas into a DataFrame.
    Cached for 5 minutes so fast page interactions don't re-query Atlas.
    """
    collection = get_collection()
    docs = list(collection.find({}, {"_id": 0}))  # _id: 0 excludes MongoDB's internal ID

    if not docs:
        return pd.DataFrame()

    df = pd.DataFrame(docs)
    df["release_year"] = pd.to_numeric(df.get("release_year"), errors="coerce")
    df["year_added"]   = pd.to_numeric(df.get("year_added"),   errors="coerce")
    df["duration_int"] = pd.to_numeric(df.get("duration_int"), errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Apply sidebar filters
# ---------------------------------------------------------------------------
def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Filter the DataFrame based on what the user selected in the sidebar."""
    fdf = df.copy()

    if filters.get("content_type") and filters["content_type"] != "All":
        fdf = fdf[fdf["type"] == filters["content_type"]]

    if filters.get("genres"):
        mask = fdf["listed_in"].apply(
            lambda x: any(g in str(x) for g in filters["genres"])
        )
        fdf = fdf[mask]

    if filters.get("countries"):
        mask = fdf["country"].apply(
            lambda x: any(c in str(x) for c in filters["countries"])
        )
        fdf = fdf[mask]

    if filters.get("year_range"):
        y1, y2 = filters["year_range"]
        fdf = fdf[(fdf["release_year"] >= y1) & (fdf["release_year"] <= y2)]

    if filters.get("ratings"):
        fdf = fdf[fdf["rating"].isin(filters["ratings"])]

    if filters.get("actor_search"):
        term = filters["actor_search"].lower()
        fdf = fdf[fdf["cast"].str.lower().str.contains(term, na=False)]

    if filters.get("director_search"):
        term = filters["director_search"].lower()
        fdf = fdf[fdf["director"].str.lower().str.contains(term, na=False)]

    return fdf

import os
import requests
import psycopg2
from dotenv import load_dotenv
import cohere

# Load .env file
load_dotenv()

# Read environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment or .env file")

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY is not set in the environment or .env file")

co = cohere.Client(COHERE_API_KEY)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def get_cohere_embedding(text: str) -> list:
    response = co.embed(texts=[text])
    embedding = response.embeddings[0]
    return embedding


def insert_job(title: str, description: str):
    embedding = get_cohere_embedding(f"{title} {description}")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO jobs (title, description, embedding)
        VALUES (%s, %s, %s)
    """, (title, description, embedding))

    conn.commit()
    cur.close()
    conn.close()

def search_jobs(query: str, limit: int = 5):
    query_embedding = get_cohere_embedding(query)

    conn = get_db_connection()
    cur = conn.cursor()

    # Assuming your DB supports vector similarity with '<=>'
    cur.execute("""
        SELECT id, title, description,
               1 - (embedding <=> %s) AS similarity
        FROM jobs
        ORDER BY embedding <=> %s
        LIMIT %s
    """, (query_embedding, query_embedding, limit))

    results = cur.fetchall()
    cur.close()
    conn.close()

    return results

import os
import requests
import psycopg2
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment or .env file")

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/embeddings")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def get_ollama_embedding(text: str) -> list:
    payload = {
        "model": "nomic-embed-text",
        "prompt": text
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    response.raise_for_status()
    data = response.json()
    emb = data.get("embedding")
    if not emb or len(emb) == 0:
        raise ValueError("Received empty embedding from Ollama API")
    return emb

def insert_job(title: str, description: str):
    embedding = get_ollama_embedding(f"{title} {description}")

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
    query_embedding = get_ollama_embedding(query)

    conn = get_db_connection()
    cur = conn.cursor()

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

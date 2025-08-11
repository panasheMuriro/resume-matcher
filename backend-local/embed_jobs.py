from embedding_utils import get_ollama_embedding
import os
import psycopg2

conn = psycopg2.connect(
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
)
cur = conn.cursor()
cur.execute("SELECT id, description FROM jobs")
jobs = cur.fetchall()


for job_id, desc in jobs:
    emb = get_ollama_embedding(desc)
    print(f"Job {job_id} embedding sample:", emb[:5])  # print first 5 values
    cur.execute("UPDATE jobs SET embedding = %s WHERE id = %s", (emb, job_id))
conn.commit()
print("Job embeddings updated.")

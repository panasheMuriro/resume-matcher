from fastapi import FastAPI, UploadFile
import psycopg2
import ast
import numpy as np
import tempfile
import os
from embedding_utils import get_ollama_embedding
from resume_utils import extract_text_from_pdf

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for React dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONN = None

def get_db_connection():
    global DB_CONN
    if DB_CONN is None:
        # Use Supabase connection URL instead of individual parameters
        DB_CONN = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    return DB_CONN

def parse_embedding(embedding_str):
    # Convert string representation of list to Python list
    emb_list = ast.literal_eval(embedding_str)
    return np.array([float(x) for x in emb_list])

def cosine_similarity(vec1_str, vec2_str):
    v1 = parse_embedding(vec1_str)
    v2 = parse_embedding(vec2_str)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

@app.post("/upload_resume")
async def upload_resume(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    resume_text = extract_text_from_pdf(tmp_path)
    embedding = get_ollama_embedding(resume_text)
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO candidates (name, resume_text, embedding) VALUES (%s, %s, %s) RETURNING id",
            ("Unknown", resume_text, embedding),
        )
        candidate_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        conn.rollback()  # Important!
        raise e
    finally:
        cur.close()
    
    return {"candidate_id": candidate_id}

@app.get("/match_jobs/{candidate_id}")
async def match_jobs(candidate_id: int):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT embedding FROM candidates WHERE id = %s", (candidate_id,))
        res = cur.fetchone()
        if not res or not res[0]:
            return {"error": "Candidate not found or has no embedding"}

        cand_emb = res[0]
        if not cand_emb:
            return {"error": "Candidate embedding is empty"}

        cur.execute("SELECT id, title, description, embedding FROM jobs WHERE embedding IS NOT NULL")
        jobs = cur.fetchall()

        matches = []
        for job in jobs:
            job_emb = job[3]
            if not job_emb:
                continue  # skip jobs without embeddings
            score = cosine_similarity(cand_emb, job_emb)
            matches.append({
                "job_id": job[0],
                "title": job[1],
                "description": job[2],
                "score": round(score, 4)
            })

        matches.sort(key=lambda x: x["score"], reverse=True)
        return {"matches": matches[:5]}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
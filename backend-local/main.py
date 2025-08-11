from fastapi import FastAPI, UploadFile
import tempfile
import os
from embedding_utils import get_ollama_embedding, get_db_connection
from resume_utils import extract_text_from_pdf
import numpy as np
import ast

app = FastAPI()

def parse_embedding(embedding_str):
    emb_list = ast.literal_eval(embedding_str)
    return np.array([float(x) for x in emb_list])

# def cosine_similarity(vec1, vec2):
#     return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
def cosine_similarity(vec1, vec2):
    v1 = np.array(vec1, dtype=float)
    v2 = np.array(vec2, dtype=float)
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
        conn.rollback()
        raise e
    finally:
        cur.close()
    
    return {"candidate_id": candidate_id}

import ast

@app.get("/match_jobs/{candidate_id}")
async def match_jobs(candidate_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT embedding FROM candidates WHERE id = %s", (candidate_id,))
    res = cur.fetchone()
    if not res or not res[0]:
        return {"error": "Candidate not found or has no embedding"}
    cand_emb_str = res[0]

    # Parse the embedding string into a list of floats
    cand_emb = ast.literal_eval(cand_emb_str) if isinstance(cand_emb_str, str) else cand_emb_str

    cur.execute("SELECT id, title, description, embedding FROM jobs WHERE embedding IS NOT NULL")
    jobs = cur.fetchall()

    matches = []
    for job in jobs:
        job_emb_str = job[3]
        if not job_emb_str:
            continue

        job_emb = ast.literal_eval(job_emb_str) if isinstance(job_emb_str, str) else job_emb_str

        score = cosine_similarity(np.array(cand_emb), np.array(job_emb))
        matches.append({
            "job_id": job[0],
            "title": job[1],
            "description": job[2],
            "score": round(score, 4)
        })

    matches.sort(key=lambda x: x["score"], reverse=True)
    cur.close()
    return {"matches": matches[:5]}

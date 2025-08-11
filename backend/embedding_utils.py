# import requests

# def get_ollama_embedding(text, model="nomic-embed-text"):
#     resp = requests.post(
#         "http://host.docker.internal:11434/api/embeddings",
#         json={"model": model, "input": text}
#     )
#     resp.raise_for_status()
#     return resp.json()["embedding"]


import requests

def get_ollama_embedding(text, model="nomic-embed-text"):
    url = "http://host.docker.internal:11434/api/embeddings"
    response = requests.post(url, json={"model": model, "prompt": text})
    response.raise_for_status()
    data = response.json()
    # Confirm the 'embedding' field exists and is a list
    embedding = data.get("embedding", [])
    if not embedding:
        raise ValueError("Received empty embedding from Ollama API")
    return embedding

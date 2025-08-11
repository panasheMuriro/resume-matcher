# # import requests

# # def get_ollama_embedding(text, model="nomic-embed-text"):
# #     resp = requests.post(
# #         "http://host.docker.internal:11434/api/embeddings",
# #         json={"model": model, "input": text}
# #     )
# #     resp.raise_for_status()
# #     return resp.json()["embedding"]


# import requests

# def get_ollama_embedding(text, model="nomic-embed-text"):
#     url = "http://host.docker.internal:11434/api/embeddings"
#     response = requests.post(url, json={"model": model, "prompt": text})
#     response.raise_for_status()
#     data = response.json()
#     # Confirm the 'embedding' field exists and is a list
#     embedding = data.get("embedding", [])
#     if not embedding:
#         raise ValueError("Received empty embedding from Ollama API")
#     return embedding


import requests
import os

def get_ollama_embedding(text, model="nomic-embed-text"):
    # Try multiple possible host addresses
    possible_hosts = [
        "host.docker.internal:11434",  # Docker Desktop on Windows/Mac
        "172.17.0.1:11434",           # Default Docker bridge gateway on Linux
        "localhost:11434",             # If running with network_mode: host
        os.environ.get("OLLAMA_HOST", "localhost:11434")  # Environment variable override
    ]
    
    for host in possible_hosts:
        try:
            url = f"http://{host}/api/embeddings"
            print(f"Trying to connect to Ollama at: {url}")
            
            response = requests.post(
                url, 
                json={"model": model, "prompt": text},
                timeout=10  # Add timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Confirm the 'embedding' field exists and is a list
            embedding = data.get("embedding", [])
            if not embedding:
                raise ValueError("Received empty embedding from Ollama API")
            
            print(f"Successfully connected to Ollama at: {host}")
            return embedding
            
        except requests.exceptions.ConnectionError as e:
            print(f"Failed to connect to {host}: {e}")
            continue
        except Exception as e:
            print(f"Error with {host}: {e}")
            continue
    
    # If all hosts failed
    raise ConnectionError(
        f"Could not connect to Ollama on any of the attempted hosts: {possible_hosts}. "
        "Make sure Ollama is running and accessible."
    )
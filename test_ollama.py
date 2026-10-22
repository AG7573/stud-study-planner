import requests

response = requests.post(
    "http://localhost:11434/api/generate", 
    json={
        "model": "llama3.2",
        "prompt": "The sky is blue.", 
        "stream": False
    }, 
    timeout=30
)

data = response.json()
print(data["response"])
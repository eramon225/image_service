import requests
import json

try:
    url = 'http://localhost:5000/images'

    payload = {
        "location": "https://www.poochandmutt.co.uk/cdn/shop/articles/download_11.jpg?v=1627313486",
        "detect": True
    }

    response = requests.post(url, json=payload)
    print(response.status_code)
    print(response.json())
except Exception as ex:
    print(f"Uncaught Exception: {ex}")

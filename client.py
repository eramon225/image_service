import requests

try:
    url = 'http://localhost:5000/images'

    payload = {
        "label": "leaf",
        "location": "C:/Users/Eric/Downloads/leaf.png",
        "detect": False
    }

    response = requests.post(url, json=payload)
    print(response.status_code)
    print(response.json())
except Exception as ex:
    print(f"Uncaught Exception: {ex}")

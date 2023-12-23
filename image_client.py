import requests
import json

url = 'http://localhost:5000/images'

payload = {
    "label": "imageLabel",
    "location": "imageLocation",
    "classify": True
}

response = requests.post( url, json=payload )
print(response.json())
import requests
import json

try:
    url = 'http://localhost:5000/images'

    payload = {
        "label": "second_label",
        "location": "https://imageio.forbes.com/specials-images/imageserve/5d35eacaf1176b0008974b54/2020-Chevrolet-Corvette-Stingray/0x0.jpg?format=jpg&crop=4560,2565,x790,y784,safe&width=960",
        "detect": True
    }

    response = requests.post(url, json=payload)
    print(response.status_code)
    print(response.json())
except Exception as ex:
    print(f"Uncaught Exception: {ex}")

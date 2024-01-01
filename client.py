import requests

def run_image(payload):
    try:
        url = 'http://localhost:5000/images'

        if "file" in payload:
            response = requests.post(url, files=payload)
        else:
            response = requests.post(url, json=payload)

        print(response.status_code)
        # print(response.json())
    except Exception as ex:
        print(f"Uncaught Exception: {ex}")

if __name__ == "__main__":
    run_image({
        "file": open( "C:/Users/Eric/Downloads/dog.jpg", "rb" )
    })
    run_image({
        "path": "C:/Users/Eric/Downloads/dog.jpg",
        "detect": False
    })
    run_image({
        "path": "https://hgtvhome.sndimg.com/content/dam/images/hgtv/fullset/2022/6/16/1/shutterstock_1862856634.jpg.rend.hgtvcom.1280.853.suffix/1655430860853.jpeg",
        "detect": False
    })



import requests
import json
import validators

def detect(image_file, api_key, api_secret):
    if validators.url(image_file):
        response = requests.get(
            'https://api.imagga.com/v2/tags?image_url=%s' % image_file,
            auth=(api_key, api_secret)
        )
        return response.json()
    else:
        response = requests.post(
            'https://api.imagga.com/v2/tags',
            auth=(api_key, api_secret),
            files={'image': image_file}
        )
        return response.json()

if __name__ == "__main__":
    print(json.dumps(detect("C:/Users/Eric/Downloads/wemby.jpg"), indent=4))

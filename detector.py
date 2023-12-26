import requests
import json
import validators

api_key = 'acc_c4be0283972f62a'
api_secret = '7327da1e5572b47ba66dd69c28790a97'

## TODO: Consider using try/except here
def detect(image_path):
    if validators.url(image_path):
        response = requests.get(
            'https://api.imagga.com/v2/tags?image_url=%s' % image_path,
            auth=(api_key, api_secret)
        )
        return response.json()
    else:
        image_file = open(image_path, 'rb')
        response = requests.post(
            'https://api.imagga.com/v2/tags',
            auth=(api_key, api_secret),
            files={'image': image_file}
        )
        return response.json()

if __name__ == "__main__":
    print(json.dumps(classify("C:/Users/Eric/Downloads/wemby.jpg"), indent=4))

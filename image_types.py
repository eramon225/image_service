import json
from collections import namedtuple
from json import JSONEncoder

class BaseImage:
    def __init__(self, location, classify, label=None):
        self.location = location
        self.label = label
        self.classify = classify

class Image(BaseImage):
    def __init__(self, id, obj, confidence, location, label, classify):
        super().__init__(location, classify, label)
        self.id = id
        self.obj = obj
        self.confidence = confidence

class ImageEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

# This is the json to class type decoder.
# I intentionally use keys here because I want
# the try/except to raise an exception if 
# there is a key missing that I deemed required
# by the object type.
def customImageDecoder(imageDict):
    try:
        # If we have an id type, we know this is a complete image
        if 'id' in imageDict:
            return Image(
                id=imageDict['id'],
                obj=imageDict['obj'],
                location=imageDict['location'],
                label=imageDict['label'],
                classify=imageDict['classify'],
                confidence=imageDict['confidence'],
            )
        else:
            return BaseImage(
                location=imageDict['location'],
                classify=imageDict.get('classify', False),
                label=imageDict.get('label', None),
            )
    except:
        raise Exception("Failed to decode json to image type!")

if __name__ == '__main__':
    # Test for base image type
    base_image_dict = {
        "location": "testLocation"
    }
    loaded_base_image = json.loads(json.dumps(base_image_dict), object_hook=customImageDecoder)
    print(type(loaded_base_image))
    print(json.dumps(loaded_base_image, indent=4, cls=ImageEncoder))

    # Test for image type
    image_dict = {
        "id": 1,
        "location": "testLocation",
        "label": "testLabel",
        "obj": "tree",
        "classify": True,
        "confidence": 80
    }
    loaded_image = json.loads(json.dumps(image_dict), object_hook=customImageDecoder)
    print(type(loaded_image))
    print(json.dumps(loaded_image, indent=4, cls=ImageEncoder))

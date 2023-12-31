import json
from dataclasses import dataclass, asdict
from typing import Optional, List
import base64

@dataclass
class ImageInput:
    path: str
    label: Optional[str] = None
    detect: Optional[bool] = True

@dataclass
class Tag:
    en: str

@dataclass
class ImageResult:
    confidence: float
    tag: Tag

@dataclass
class _Image:
    id: int
    objects: List[ImageResult]
    data: str

@dataclass
class Image(ImageInput, _Image):
    pass

if __name__ == '__main__':
    # Test for base image type
    image_input_dict = {
        "path": "testpath",
        "label": "testLabel"
    }
    f = open('C:/Users/Eric/Downloads/leaf.png', 'rb')
    image_bytes = f.read()
    image_dict = {
        "id": 1,
        "path": "testpath",
        "label": "testLabel",
        "objects": [{
            "confidence": 100,
            "tag": {
                "en": "basketball"
            }
        },
        {
            "confidence": 100,
            "tag": {
                "en": "basketball equipment"
            }
        }],
        "detect": True,
        "data": base64.b64encode(image_bytes).decode('ascii')
    }

    image_input = ImageInput(**image_input_dict)
    print(image_input)
    print(json.dumps(asdict(image_input), indent=4))
    image = Image(**image_dict)
    print(image)
    print(json.dumps(asdict(image), indent=4))



import json
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class ImageInput:
    location: str
    label: Optional[str] = None
    classify: Optional[bool] = True

@dataclass
class _Image:
    id: int
    obj: str
    confidence: float

@dataclass
class Image(ImageInput, _Image):
    pass

if __name__ == '__main__':
    # Test for base image type
    image_input_dict = {
        "location": "testLocation",
        "label": "testLabel"
    }
    image_dict = {
        "id": 1,
        "location": "testLocation",
        "label": "testLabel",
        "obj": "tree",
        "classify": True,
        "confidence": 80
    }

    image_input = ImageInput(**image_input_dict)
    print(image_input)
    print(json.dumps(asdict(image_input), indent=4))
    image = Image(**image_dict)
    print(image)
    print(json.dumps(asdict(image), indent=4))



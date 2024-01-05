# Python REST Service

This repository contains a Python-based RESTful service that provides Imagga recognition for images.

## Features

- **Query Images and metadata** GET all image data stored in a database. /images
- **Query Images associated with object** GET images that are recognized to be associated with given objects. /images?objects="dog,cat"
- **Query Image with matching Id** GET image that has matching Id. /images/1
- **POST Image** POST image with a url, file location, or multipart/forum. /images

### Prerequisites

- Python (version >= 3.11)
- flask
- flask_cors
- json
- psycopg2
- traceback
- validators
- requests
- base64
- dataclasses
- pyyaml

### Usage

`python rest.py`

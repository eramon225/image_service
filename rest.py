
from flask import Flask, request
from flask_cors import CORS
import json
import psycopg2
import traceback
import validators
import requests
import base64

from image_types import ImageInput, Image
from detector import detect
from dataclasses import asdict

import yaml

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

app = Flask(__name__)
## Allow POST requests from GUI
CORS(app)

conn = psycopg2.connect(
            host=config['db']['host'],
            database=config['db']['database'],
            user=config['db']['user'],
            password=config['db']['password']
        )

api_key = config['api']['api_key']
api_secret = config['api']['api_secret']

# create a cursor
cur = conn.cursor()

ID_INCREMENT = 1

BASE_TABLE_NAME = "Images8"
TABLE_NAME = 'public."%s"'%BASE_TABLE_NAME

COLUMNS = "id, path, label, objects, detect, data"
ORDER = "ORDER BY id ASC"

table_sql = f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME}
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT {ID_INCREMENT} ),
    label character varying(256) NOT NULL UNIQUE,
    path character varying(256) NOT NULL,
    objects jsonb,
    detect boolean NOT NULL,
    data bytea NOT NULL,
    PRIMARY KEY (id)
);"""

# execute sql while applying a rollback incase
# errors occur during the transaction.
try:
    cur.execute(table_sql)
    conn.commit()
except Exception as ex:
    print(ex)
    conn.rollback()

def to_image(res):
    return Image(
        id=res[0],
        path=res[1],
        label=res[2],
        objects=res[3],
        detect=res[4],
        data=base64.b64encode(res[5]).decode('ascii')
    )

def parse_result(query_results):
    try:
        results = []
        for res in query_results:
            image = to_image(res)
            results.append(asdict(image))
        return results
    except Exception as ex:
        raise Exception(f"Parsing exception {ex}")

def get_all_images():
    query_str = f"SELECT {COLUMNS} FROM {TABLE_NAME} {ORDER}"
    cur.execute(query_str)
    query_results = cur.fetchall()
    return json.loads(json.dumps(parse_result(query_results)))

def get_images_by_object(objects_str):
    objects_array = objects_str.split(',')

    # The query below selects by doing
    # a cross join on the 'objects' jsonb field
    # so we can evaluate each entry in the jsonb
    # array to see what objects match.
    query_str = f"""SELECT {COLUMNS}
                    FROM {TABLE_NAME}
                    CROSS JOIN LATERAL jsonb_array_elements(
                        case jsonb_typeof(objects) 
                            when 'array' then objects 
                            else '[]' end
                        ) as obj
                    WHERE """
    for idx in range(len(objects_array)):
        obj = objects_array[idx]
        query_str += "obj ->> 'tag' = '{\"en\": \"%s\"}' "%str(obj)
        if idx != len( objects_array ) - 1:
            query_str += 'OR '
    query_str += f' {ORDER};'
    cur.execute(query_str)
    query_results = cur.fetchall()
    return json.loads(json.dumps(parse_result(query_results)))

def get_images_by_id(id):
    query_str = f"SELECT {COLUMNS} FROM {TABLE_NAME} WHERE id = {id};"
    cur.execute(query_str)
    res = cur.fetchone()
    image = to_image(res)
    # Returning simply "asdict(image)" would work as well
    # but to be completely sure we're returning a json,
    # we'll wrap it with a json dumps and loads.
    return json.loads(json.dumps(asdict(image)))

def get_image_bytes(image_path):
    if validators.url(image_path):
        # Download the bytes from the url
        image_bytes = requests.get(image_path, stream=True)
        return image_bytes.content
    else:
        # Read the bytes from the image path locally
        image_file = open(image_path, 'rb')
        image_bytes = image_file.read()
        return image_bytes

def post_image(input_dict):
    try:
        classifier_result = None
        if "file" in input_dict:
            image_file = input_dict["file"]
            image_bytes = image_file.read()
            image_input = ImageInput(
                path=image_file.filename,
                label=None,
                detect=True
            )
        else:
            image_input = ImageInput(**input_dict)

            # Get the image bytes to store into the database
            image_bytes = get_image_bytes(image_input.path)    

        if image_input.detect == True:
            try:
                res = detect(image_bytes, api_key, api_secret)
            except Exception as ex:
                raise Exception(f"detector {ex}")
            # only get the results if the query is a success
            if res['status']['type'] == 'success':
                classifier_result = res["result"]["tags"]
            elif res['status']['type'] == 'error':
                error_messsage = res['status']['text']
                raise Exception(f" detector {error_messsage}")

        # If our label is None, we'll assign something
        if image_input.label == None:
            # The query below checks what the current id value
            # for the sequence is, and then, add the increment
            # value when the sequence "is_called".
            # So for the first row, no sequence is called, resulting
            # in the "last_value" == 1. On the second row, "is_called" becomes true
            # since the sequence next_value under the hood was called,
            # but "last_value" still == 1, however we can 
            # work around it by checking the "is_called",
            # and increment from there.
            query_str = f"""SELECT
                            last_value + CASE WHEN is_called THEN {ID_INCREMENT} ELSE 0 END
                            FROM \"{BASE_TABLE_NAME}_id_seq\";"""
            cur.execute(query_str)
            id = cur.fetchone()[0]

            # If we screened this image, use the best 
            # result as the label if we were not provided
            # a label to use for the database.
            if classifier_result is not None and len(classifier_result) > 0:
                best_label = classifier_result[0]['tag']['en']
                image_input.label = f"{best_label}_{id}"
            else:
                image_input.label = f"undetected_{id}"

        # The '%s' below is for the image data
        query_str = f"""INSERT INTO {TABLE_NAME}(path, label, objects, detect, data) 
                        VALUES ('{image_input.path}', '{image_input.label}', '{json.dumps(classifier_result)}'::jsonb,
                                 {str(image_input.detect)}, %s)
                        RETURNING {COLUMNS};"""
        try:
            cur.execute(query_str, (image_bytes,))
            db_return = cur.fetchone()

            # Create our Image object from the result of the database
            # to ensure we're on the same page of what was just inserted.
            image = to_image(db_return)

            conn.commit()
            return json.loads(json.dumps(asdict(image)))
        except Exception as ex:
            conn.rollback()
            raise Exception(f"{ex}")
    except Exception as ex:
        print(traceback.print_exc())
        raise Exception(f"POST Image exception {ex}")

@app.route("/images", methods=["GET", "POST"])
def get_images():
    try:
        if request.method == "POST":
            # Handle multipart-form here
            if 'file' in request.files:
                return post_image(request.files)
            else:
                return post_image(json.loads(request.data))
        elif request.method == "GET":
            objects_str = request.args.get("objects", None)
            # If the objects variable fell back to None,
            # we know this is a regular GET for images.
            if objects_str:
                return get_images_by_object(objects_str)
            else:
                return get_all_images()
    except Exception as ex:
        print(ex)
        return error_response(f"Uncaught {ex}")
    return error_response("Method was not recognized")
    
@app.route("/images/<id>")
def get_image(id):
    try:
        return get_images_by_id(id)
    except Exception as ex:
        return error_response(f"Uncaught {ex}")

def error_response(msg):
    return json.loads(json.dumps({"ERROR": msg})), 400
    
if __name__ == "__main__":
    app.run()
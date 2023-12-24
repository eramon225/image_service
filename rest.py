
from flask import Flask, request
import json
import psycopg2

from image_types import ImageInput, Image
from image_classifier import classifyImage
from dataclasses import asdict

app = Flask(__name__)

conn = psycopg2.connect(
            host="localhost",
            database="NewDB",
            user="postgres",
            password="1234"
        )
		
# create a cursor
cur = conn.cursor()

BASE_TABLE_NAME = "Images2"
TABLE_NAME = 'public."%s"'%BASE_TABLE_NAME

COLUMNS = "id, location, label, object, classify, confidence"

OPTIONS = ["daisy", "dandelion", "roses", "sunflowers", "tulips"]

def parse_result(query_results):
    try:
        results = []
        for res in query_results:
            image = Image(
                id=res[0],
                location=res[1],
                label=res[2],
                obj=res[3],
                classify=res[4],
                confidence=res[5]
            )
            results.append(asdict(image))
        return results
    except Exception as ex:
        raise Exception(f"Parsing exception {ex}")

def get_all_images():
    query_str = f"SELECT {COLUMNS} FROM {TABLE_NAME}"
    cur.execute(query_str)
    query_results = cur.fetchall()
    return json.loads(json.dumps(parse_result(query_results)))

def get_images_by_object(objects_str):
    objects_array = objects_str.split(',')
    query_str = f"SELECT {COLUMNS} FROM {TABLE_NAME} WHERE "
    for idx in range(len(objects_array)):
        obj = objects_array[idx]
        query_str += 'object = \'%s\' '%obj
        if idx != len( objects_array ) - 1:
            query_str += 'OR '
    query_str += ';'
    cur.execute(query_str)
    query_results = cur.fetchall()
    return json.loads(json.dumps(parse_result(query_results)))

def get_images_by_id(id):
    query_str = f"SELECT {COLUMNS} FROM {TABLE_NAME} WHERE id = {id};"
    cur.execute(query_str)
    query_results = cur.fetchone()
    result = {"id": query_results[0], "label": query_results[1], "object": query_results[2]}
    return json.loads(json.dumps(result))

def post_image(input_dict):
    try:
        image_input = ImageInput(**input_dict)
        obj = None
        confidence = None

        if image_input.classify == True:
            res = classifyImage(image_input.location, OPTIONS)
            obj = res["obj"]
            confidence = res["confidence"]

        # If our label is None, we'll assign something
        if image_input.label == None:
            # Lookup the id we'll use from the database
            query_str = f"SELECT last_value FROM \"{BASE_TABLE_NAME}_id_seq\";"
            cur.execute(query_str)
            # increment to match what the entry will be.
            id = cur.fetchone()[0] + 1

            if obj is not None:
                image_input.label = f"{obj}_{id}"
            else:
                image_input.label = f"unclassified_{id}"
        # If an object object was not classified, just
        # use a null string.
        obj_input = f"'{obj}'" if obj is not None else "NULL"
        confidence = str(confidence) if confidence is not None else "NULL"
        query_str = f"""INSERT INTO {TABLE_NAME}(location, label, object, classify, confidence) 
                        VALUES ('{image_input.location}', '{image_input.label}', {obj_input},
                                 {str(image_input.classify)}, {str(confidence)})
                        RETURNING {COLUMNS};"""
        cur.execute(query_str)
        db_return = cur.fetchone()

        # Create our Image object from the result of the database
        # to ensure we're on the same page of what was just inserted.
        image = Image(
            id=db_return[0],
            location=db_return[1],
            label=db_return[2],
            obj=db_return[3],
            classify=db_return[4],
            confidence=db_return[5]
        )

        conn.commit()
        return json.dumps(asdict(image), indent=4)
    except Exception as ex:
        raise Exception(f"POST Image exception {ex}")

@app.route("/images", methods=["GET", "POST"])
def get_images():
    try:
        if request.method == "POST":
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
    return error_response("Complete GET for image id but something may have gone wrong.")

def error_response(msg):
    return json.loads(json.dumps({"ERROR": msg})), 400
    
if __name__ == "__main__":
    app.run()

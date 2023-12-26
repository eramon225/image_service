
from flask import Flask, request
import json
import psycopg2
import traceback

from image_types import ImageInput, Image
from detector import detect
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

BASE_TABLE_NAME = "Images6"
TABLE_NAME = 'public."%s"'%BASE_TABLE_NAME

COLUMNS = "id, path, label, objects, detect"

table_sql = f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME}
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 ),
    label character varying(256) NOT NULL UNIQUE,
    path character varying(256) NOT NULL,
    objects jsonb,
    detect boolean NOT NULL,
    PRIMARY KEY (id)
);"""

# execute sql while applying a rollback incase
# errors occur during the transaction.
try:
    cur.execute(sql)
    conn.commit()
except Exception as ex:
    print(ex)
    conn.rollback()

def parse_result(query_results):
    try:
        results = []
        for res in query_results:
            image = Image(
                id=res[0],
                location=res[1],
                label=res[2],
                objects=res[3],
                detect=res[4],
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
    query_str = f"""SELECT i.id, i.objects, i.label, i.path, i.detect
                    FROM {TABLE_NAME} i
                    CROSS JOIN LATERAL jsonb_array_elements(i.objects) o(obj)
                    WHERE """
    for idx in range(len(objects_array)):
        obj = objects_array[idx]
        query_str += "o.obj ->> 'tag' = '{\"en\": \"%s\"}' "%str(obj)
        if idx != len( objects_array ) - 1:
            query_str += 'OR '
    query_str += ';'
    cur.execute(query_str)
    query_results = cur.fetchall()
    return json.loads(json.dumps(parse_result(query_results)))

def get_images_by_id(id):
    query_str = f"SELECT {COLUMNS} FROM {TABLE_NAME} WHERE id = {id};"
    cur.execute(query_str)
    res = cur.fetchone()
    image = Image(
                id=res[0],
                location=res[1],
                label=res[2],
                objects=res[3],
                detect=res[4],
            )
    # Returning simply "asdict(image)" would work as well
    # but to be completely sure we're returning a json,
    # we'll wrap it with a json dumps and loads.
    return json.loads(json.dumps(asdict(image)))

def post_image(input_dict):
    try:
        image_input = ImageInput(**input_dict)
        classifier_result = None
        confidence = None
        if image_input.detect == True:
            try:
                res = detect(image_input.location)
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
            # Lookup the id we'll use from the database
            query_str = f"SELECT last_value FROM \"{BASE_TABLE_NAME}_id_seq\";"
            cur.execute(query_str)
            # increment to match what the entry will be.
            id = cur.fetchone()[0] + 1

            # If we screened this image, use the best 
            # result as the label if we were not provided
            # a label to use for the database.
            if classifier_result is not None and len(classifier_result) > 0:
                best_label = classifier_result[0]['tag']['en']
                image_input.label = f"{best_label}_{id}"
            else:
                image_input.label = f"undetected_{id}"

        query_str = f"""INSERT INTO {TABLE_NAME}(path, label, objects, detect) 
                        VALUES ('{image_input.location}', '{image_input.label}', '{json.dumps(classifier_result)}'::jsonb,
                                 {str(image_input.detect)})
                        RETURNING {COLUMNS};"""

        try:
            cur.execute(query_str)
            db_return = cur.fetchone()

            # Create our Image object from the result of the database
            # to ensure we're on the same page of what was just inserted.
            image = Image(
                id=db_return[0],
                location=db_return[1],
                label=db_return[2],
                objects=db_return[3],
                detect=db_return[4],
            )

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
                pass
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
    return error_response("Complete GET for image id but something may have gone wrong.")

def error_response(msg):
    return json.loads(json.dumps({"ERROR": msg})), 400
    
if __name__ == "__main__":
    app.run()
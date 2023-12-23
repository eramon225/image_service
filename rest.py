
from flask import Flask, request
import json
import psycopg2

from image_types import BaseImage, Image, customImageDecoder, ImageEncoder

app = Flask(__name__)

conn = psycopg2.connect(
            host="localhost",
            database="NewDB",
            user="postgres",
            password="1234"
        )
		
# create a cursor
cur = conn.cursor()

TABLE_NAME = 'public."Images2"'

def getAllImages():
    query_str = 'SELECT id, label, object FROM %s'%TABLE_NAME
    cur.execute(query_str)
    query_results = cur.fetchall()
    results = []
    for res in query_results:
        i = {'id': res[0], 'label': res[1], 'object': res[2]}
        results.append(i)
    return json.loads(json.dumps(results))

def getImagesByObject(objects_str):
    objects_array = objects_str.split(',')
    query_str = 'SELECT id, label, object FROM %s WHERE '%TABLE_NAME
    for idx in range(len(objects_array)):
        obj = objects_array[idx]
        query_str += 'object = \'%s\' '%obj
        if idx != len( objects_array ) - 1:
            query_str += 'OR '
    query_str += ';'
    cur.execute(query_str)
    query_results = cur.fetchall()
    results = []

    for res in query_results:
        i = {'id': res[0], 'label': res[1], 'object': res[2]}
        results.append(i)
    return json.loads(json.dumps(results))

def getImageById(id):
    query_str = 'SELECT id, label, object FROM %s WHERE id = %s;'%(TABLE_NAME,str(id))
    cur.execute(query_str)
    query_results = cur.fetchall()
    results = []
    for res in query_results:
        i = {'id': res[0], 'label': res[1], 'object': res[2]}
        results.append(i)
    return json.loads(json.dumps(results))

@app.route('/images', methods=['GET', 'POST'])
def getImages():
    try:
        if request.method == 'POST':
            base_image = json.loads(request.data, object_hook=customImageDecoder)
            confidence = 88.5
            if base_image.label == None:
                base_image.label = 'tempLabel'
            obj = 'tree'
            query_str = 'INSERT INTO %s(location, label, object, classify, confidence) \
                         VALUES (\'%s\', \'%s\', \'%s\', %s, %s) RETURNING id;'%(
                            TABLE_NAME,
                            base_image.location,
                            base_image.label,
                            obj,
                            str(base_image.classify),
                            str(confidence)
                        )
            cur.execute( query_str )

            id = cur.fetchone()[0]
            image = Image(
                id=id,
                location=base_image.location,
                label=base_image.label,
                obj=obj,
                classify=base_image.classify,
                confidence=confidence
            )

            conn.commit()
            return json.loads(json.dumps(image, indent=4, cls=ImageEncoder))
        elif request.method == 'GET':
            objects_str = request.args.get('objects', None)
            # If the objects variable fell back to None,
            # we know this is a regular GET for images.
            if objects_str:
                return getImagesByObject(objects_str)
            else:
                return getAllImages()
    except Exception as ex:
        print(ex)
        return json.dumps({'message': 'Uncaught exception %s'%str(ex)})
    return json.dumps({'message': 'this method was not recognized'})
    
    
@app.route('/images/<id>')
def getImage(id):
    try:
        return getImageById(id)
    except Exception as ex:
        return json.dumps({'message': 'Uncaught exception %s'%str(ex)})
    return json.dumps({'message': 'Complete GET for image id but something may have gone wrong.'})
    
if __name__ == '__main__':
    app.run()
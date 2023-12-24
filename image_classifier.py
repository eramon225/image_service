
import tensorflow as tf
from keras.models import load_model
import numpy as np

img_height = 180
img_width = 180
class_names = ['daisy', 'dandelion', 'roses', 'sunflowers', 'tulips']
model = load_model('flower_model.h5')
 
# Predict using the model
sunflower_url = "https://storage.googleapis.com/download.tensorflow.org/example_images/592px-Red_sunflower.jpg"

def classifyImage(url, options):
    sunflower_path = tf.keras.utils.get_file(origin=url)

    img = tf.keras.utils.load_img(
        sunflower_path, target_size=(img_height, img_width)
    )
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) # Create a batch

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    return {'obj': options[np.argmax(score)], 'confidence': 100 * np.max(score)}

if __name__ == "__main__":
    result = classifyImage( sunflower_url, class_names )

    print(
        "This image most likely belongs to {} with a {:.2f} percent confidence."
        .format(result['obj'], result['confidence'])
    )

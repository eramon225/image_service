
import tensorflow as tf
from keras.models import load_model
import numpy as np

img_height = 180
img_width = 180
class_names = ['daisy', 'dandelion', 'roses', 'sunflowers', 'tulips']
model = load_model('flower_model.h5')
 
# Predict using the model
#sunflower_url = "https://storage.googleapis.com/download.tensorflow.org/example_images/592px-Red_sunflower.jpg"
#sunflower_url = "https://s3.amazonaws.com/cdn.tulips.com/images/popup/Jumbo-Pink-Triumph-Tulip-close-up.jpg"
sunflower_url = "https://imageio.forbes.com/specials-images/imageserve/6064b148afc9b47d022718d1/Hennessey-Venom-F5/960x0.jpg?height=473&width=711&fit=bounds"
sunflower_path = tf.keras.utils.get_file(origin=sunflower_url)

img = tf.keras.utils.load_img(
    sunflower_path, target_size=(img_height, img_width)
)
img_array = tf.keras.utils.img_to_array(img)
img_array = tf.expand_dims(img_array, 0) # Create a batch

predictions = model.predict(img_array)
score = tf.nn.softmax(predictions[0])

print(
    "This image most likely belongs to {} with a {:.2f} percent confidence."
    .format(class_names[np.argmax(score)], 100 * np.max(score))
)
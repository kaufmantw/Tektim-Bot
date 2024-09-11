from tensorflow.keras.preprocessing import image
import numpy as np

# format image to be 256x256 b/w
def create_img_data(filepath):
    img = image.load_img(filepath, target_size=(256, 256))
    img_arr = image.img_to_array(img)
    img_arr = np.expand_dims(img_arr, axis=0)
    return img_arr
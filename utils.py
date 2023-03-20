from PIL import Image

import numpy as np

def get_image_vector(required_image_size, image_path):

    image_size = required_image_size

    im = Image.open(image_path)
    im = im.resize((image_size, image_size), resample = Image.Resampling.BILINEAR)

    data = np.array(im)

    return data

def predict(model, data):

    return model.predict(np.expand_dims(data, axis = 0))
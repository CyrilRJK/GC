import tensorflow as tf
import multiprocessing
import SimpleITK
from skimage import transform
from PIL import Image
import numpy as np

from evalutils import SegmentationAlgorithm
from evalutils.validators import (
    UniquePathIndicesValidator,
    UniqueImagesValidator,
)

def extractCenterPatch(input_image):

    h, w, c = input_image.shape
    x_min = h // 2 - 284 // 2
    y_min = w // 2 - 284 // 2    
    patch = input_image[x_min:x_min+284, y_min:y_min+284]
    return patch

class BCSSSegmentation(SegmentationAlgorithm):
    def __init__(self):
        super().__init__(
            validators=dict(
                input_image=(
                    UniqueImagesValidator(),
                    UniquePathIndicesValidator(),
                )
            ),
        )

        self.model = tf.keras.models.load_model(f"./model/hooknet2", 
                                   compile=True)

    def write_outputs(self, image):
        SimpleITK.WriteImage(image, 'output/output.tif')


    def predict(self, input_image):
        image = SimpleITK.GetArrayFromImage(input_image)
        image = np.array(image)
        patch = extractCenterPatch(image)

        # Pre-process the image
        image = transform.resize(image, (284, 284), order=3)
        x = np.array([patch, image])
        x = x.reshape(2, 1, 284, 284, 3)
        x = [x[0], x[1]]
        
        # Predict
        prediction = model.predict(x) 
        prediction = prediction[0]
        prediction_root = int(np.sqrt(prediction.shape[1]))
        prediction = prediction.reshape(prediction_root, prediction_root, prediction.shape[2])
        
        out = (prediction * 255).astype(np.uint8)
        out = SimpleITK.GetImageFromArray(out)
        return out


if __name__ == "__main__":
    BCSSSegmentation().process()
import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

# keras imports
# from keras.applications.vgg16 import VGG16, preprocess_input
# from keras.applications.vgg19 import VGG19, preprocess_input
# from keras.applications.xception import Xception, preprocess_input
# from keras.applications.resnet50 import ResNet50, preprocess_input
# from keras.applications.inception_resnet_v2 import InceptionResNetV2, preprocess_input
# from keras.applications.mobilenet import MobileNet, preprocess_input
from keras.applications.inception_v3 import preprocess_input
from keras.preprocessing import image
from keras.models import model_from_json
import dbquery
import numpy as np
import argparse
import pickle

model_json_file="/Users/pranoy/Desktop/medi-fi/ml/model.json"
model_weights_file="/Users/pranoy/Desktop/medi-fi/ml/model.h5"
classifier_file="/Users/pranoy/Desktop/medi-fi/ml/classifier_LogisticReg.pickle"
labelencoder_file="/Users/pranoy/Desktop/medi-fi/ml/LabelEncoder.pickle"
# ima
image_size = (299, 299)

def get_model():
	# load json and create model
	json_file = open(model_json_file, 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	model = model_from_json(loaded_model_json)
	# load weights into new model
	model.load_weights(model_weights_file)
	print("Loaded model from disk")
	return model
def get_features(model,image_path):
	img = image.load_img(image_path,target_size=image_size)
	x = image.img_to_array(img)
	x = np.expand_dims(x, axis=0)
	x = preprocess_input(x)
	feature = model.predict(x)
	flat = feature.flatten()
	return flat
model=get_model()
model.summary()
classifier = pickle.load(open(classifier_file, 'rb'))
# keep this much loaded always
parser = argparse.ArgumentParser()
parser.add_argument("Image_path")
args = parser.parse_args()
image_path = args.Image_path
feature=get_features(model,image_path)
result=classifier.predict(np.asarray(feature).reshape(1, -1))
le = pickle.load(open(labelencoder_file, 'rb'))
res=le.inverse_transform(result)
print(res[0])
string1 = image_path.split('/')
path1 = string1[len(string1)-1]

sql="update posts set tag='%s' where image='%s' "%(res[0],path1)
dbquery.inserttodb(sql)



import random
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import requests
import shutil
import os
import numpy as np

#image prediction with resnet50 model
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from dataset_tools.img_cleaner import create_img_data
import joblib

def generate_response(msg):
    '''
    Two types of messages should be send:
        1. When a message with <3 words is sent, send a predetermined message
        2. When a message with >=3 words is sent, send x on my y till she z
    '''
    msg_options = ['nyuck',
                   'shut up',
                   'hello habibi']
    
    stop_words = set(stopwords.words('english'))
    msg = re.sub(r'[^\w\s?!]', '', msg)
    msg = word_tokenize(msg) #this is... slow?
    filtered_sentence = [word for word in msg if word.lower() not in stop_words]

    # if the message is long enough, return this premade sentence
    if len(filtered_sentence) >= 3:
        random_words = random.sample(filtered_sentence, 3)
        response = "she " + random_words[0] + " on my " + random_words[1] + " till i " + random_words[2]

    # if there is no content (message is just a ping) return ?
    elif len(msg) == 0:
        response = "?"
    
    # otherwise, choose a random message choice
    else:
        response = random.choice(msg_options)
    return response

def generate_react_on_media(attachment, model):
    # catchest:        <:catchest:1267111295145087057>
    # erm:             <:erm:1267111273275854908>
    # golden catchest: <:golden_catchest:1268418504990654546>

    attachment = attachment[0]
    reaction = ''

    # if the attachment is an image, we are going to predict on it
    print(attachment.content_type)
    if attachment.content_type.startswith("image/"):

        #download the image
        download_image(attachment.url, attachment.filename)

        #create image data
        path = "C:\\Users\\timka\\Documents\\code\\python\\Tektim-Bot\\data\\images\\live_input\\" + attachment.filename 
        x_test = create_img_data(path)

        #predict using the model
        try:
            prediction = model.predict(x_test)
        except Exception as e:
            print(f"Error caught: {e}")

        # assign reaction off prediction
        class_names = joblib.load('data\models\pred_names\class_names.pkl')
        prediction = class_names[np.argmax(prediction)]

        print("Prediction: ",prediction)
        if prediction == "funny":
            rng = random.randrange(1, 1000)
            if rng == 1:
                reaction = "<:golden_catchest:1268418504990654546>"
            else:
                reaction = "<:catchest:1267111295145087057>"
        elif prediction == "cringe":
            reaction = "<:erm:1267111273275854908>"
        else:
            reaction = "<:clueless:1267111395498004532>"

    # if the attachment is not an image, do default reacting
    else:
        rng = random.randrange(1, 10)
        if rng == 1:
            rng2 = random.rangrange(1, 1000)
            if rng2 == 1:
                reaction = "<:golden_catchest:1268418504990654546>"
            else:
                reaction = "<:catchest:1267111295145087057>"
        elif rng == 2:
            reaction = "<:erm:1267111273275854908>"
        else:
            reaction = "<:clueless:1267111395498004532>"
            
    # when prediction is done, delete the image from live_input
    os.remove(path)

    return reaction

def check_dogness(avatar, model):
    pic_url = avatar.url
    file_name = avatar.key

    download_image(pic_url, file_name)

    path = "C:\\Users\\timka\\Documents\\code\\python\\Tektim-Bot\\data\\images\\live_input\\" + file_name
    x_test = create_img_data(path)

    #predict using the model
    try:
        prediction = model.predict(x_test)
    except Exception as e:
        print(f"Error caught: {e}")

    # assign reaction off prediction
    class_names = joblib.load('data/models/pred_names/dogcat_names.pkl')
    prediction = class_names[np.argmax(prediction)]

    print("Prediction: ",prediction)
    if prediction == 'cats':
        response = 'You ain\'t a dog lil bro'
    else:
        response = 'big dawg'
    # remove when done
    os.remove(path)
    return response

def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        dir = "C:\\Users\\timka\\Documents\\code\\python\\Tektim-Bot\\data\\images\\live_input"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f'Downloaded {filename}')

        # move the file to the correct folder
        shutil.move(filename, dir)

    else:
        print(f'Failed to download {filename}')


try:
    nltk.data.find('corpora/stopwords')  # Check if 'stopwords' is available
    print("'stopwords' is already downloaded.")
except LookupError:
    nltk.download('stopwords')
    print("'stopwords' has been downloaded.")

try:
    nltk.data.find('tokenizers/punkt')  # Check if 'punkt' is available
    print("'punkt' is already downloaded.")
except LookupError:
    nltk.download('punkt')
    print("'punkt' has been downloaded.")
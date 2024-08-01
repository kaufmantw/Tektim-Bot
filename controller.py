import random
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import joblib
import requests
import shutil
import os

#image prediction and processing imports
from sklearn.svm import SVC
from dataset_tools.img_cleaner import create_img_data

def generate_response(msg):
    '''
    Two types of messages should be send:
        1. When a message with <3 words is sent, send a predetermined message
        2. When a message with >=3 words is sent, send x on my y till she z
    '''
    msg_options = ['nyuck',
                   '?',
                   'shut up']
    
    stop_words = set(stopwords.words('english'))
    msg = re.sub(r'[^\w\s?!]', '', msg)
    msg = word_tokenize(msg) #this is... slow?
    filtered_sentence = [word for word in msg if word.lower() not in stop_words]

    if len(filtered_sentence) >= 3:
        random_words = random.sample(filtered_sentence, 3)
        response = "she " + random_words[0] + " on my " + random_words[1] + " till i " + random_words[2]
    else:
        response = random.choice(msg_options)
    return response

def generate_react_on_media(attachment):
    #If an image is sent, for now respond with an emote. 10 10 80 split
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
        x_test = x_test.reshape(1, -1)
        #grab the model
        model = joblib.load('data/models/256img_model.joblib')

        #predict using the model
        try:
            prediction = model.predict(x_test)
        except Exception as e:
            print(f"Error caught: {e}")

        # assign reaction off prediction
        print("Prediction: ",prediction)
        match prediction:
            case "funny":
                rng2 = random.randrange(1, 100)
                if rng2 == 1:
                    reaction = "<:golden_catchest:1268418504990654546>"
                else:
                    reaction = "<:catchest:1267111295145087057>"
            case "cringe":
                reaction = "<:erm:1267111273275854908>"

    # if the attachment is not an image, do default reacting
    else:
        rng = random.randrange(1, 10)
        match rng:
            case 1:
                rng2 = random.randrange(1, 100)
                if rng2 == 1:
                    reaction = "<:golden_catchest:1268418504990654546>"
                else:
                    reaction = "<:catchest:1267111295145087057>"
            case 2:
                reaction = "<:erm:1267111273275854908>"

    # when prediction is done, delete the image from live_input
    os.remove(path)

    return reaction

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


nltk.download('stopwords')
nltk.download('punkt')
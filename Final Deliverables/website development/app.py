import os
import uuid
import flask
import urllib
from PIL import Image
from tensorflow.keras.models import load_model
from flask import Flask , render_template  , request , send_file
from tensorflow.keras.preprocessing.image import load_img , img_to_array
import cv2

app = Flask(__name__)


MODEL_PATH = 'models/Disaster_Classifier.h5'

model = load_model(MODEL_PATH)  
ALLOWED_EXT = set(['jpg' , 'jpeg' , 'png' , 'jfif', 'mp4'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT

classes = ['Cyclone','Earthquake','Flood','Wildfire']


def predict(filename , model):
    img = load_img(filename , target_size = (299 , 299))
    img = img_to_array(img)
    img = img.reshape(1 , 299 ,299 ,3)

    img = img.astype('float32')
    img = img/255.0
    result = model.predict(img)

    dict_result = {}
    for i in range(4):
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:4]
    
    prob_result = []
    class_result = []
    for i in range(4):
        prob_result.append((prob[i]*100).round(2))
        class_result.append(dict_result[prob[i]])

    return class_result , prob_result


def predict_from_video(filename , model):
    target_img = os.path.join(os.getcwd(), 'static', 'uploads')
    video_cap = cv2.VideoCapture(os.path.join(target_img , filename))
    cls = {}
    while True:
        success, frame = video_cap.read()
        if not success:
            break
        
        frame = cv2.resize(frame, (299 ,299))
        img = frame.reshape(1 , 299 ,299 ,3)

        img = img.astype('float32')
        img = img/255.0
        result = model.predict(img).tolist()
        result = result[0]
        print(result)
        
        try:
            cls[result.index(max(result))] += 1
        except:
            cls[result.index(max(result))] = 1

    video_cap.release()

    print(cls.items())
    x = sorted(cls.items(), key=lambda x:x[1])

    return classes[x[-1][0]]


@app.route('/')
def home():
    return render_template('homepage.html', title='Disaster Classifier | Home', active_page='home')

@app.route('/intro')
def intro():
    return render_template('intro.html', title='Disaster Classifier | About', active_page='intro')

@app.route('/weather')
def weather():
    return render_template('weather.html', title='Weather Forecast', active_page='weather')
@app.route('/launch')
def launch():
        return render_template('launch.html', title='Disaster Classfier | Launch', active_page='launch')

@app.route('/success' , methods = ['GET' , 'POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd(), 'static', 'uploads')
    if request.method == 'POST':
        if(request.form):
            link = request.form.get('link')
            try :
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename+".jpg"
                img_path = os.path.join(target_img , filename)
                output = open(img_path , "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result , prob_result = predict(img_path , model)

                predictions = {
                      "class1":class_result[0],
                        "class2":class_result[1],
                        "class3":class_result[2],
                        "class4":class_result[3],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                        "prob4": prob_result[3]
                }
                final_res = class_result[prob_result.index(max(prob_result))]
                if final_res=="Flood":
                    measures = 'Seek Higher Grounds during Floods, and donot wait for any Instructions. Be aware of Flash flood areas such as canals, drainage channels, etc. Turn off any Electrical Appliances, and avoid driving during floods. Be ready to Evacuate.'
                elif final_res=="Wildfire":
                    measures = 'To prevent wildfires, it is essential to undertake technical checkups regularly. have properly functioning spark arrestors. never park near dry grass, especially, close to forests. have a shovel and a fire-extinguisher. carry a bucket or anything suitable to fill with water. store a reservoir with water or sand.'
                elif final_res=="Cyclone":
                    measures = 'Be aware of the official cyclone warning by listening to the radio or other authentic sources. Install storm shutters or board up glass windows. Keep all the doors and windows closed. Switch off the electrical mains in your house. Stay away from concrete walls and floors because thunder lightning can pass through the metal bars in them.'
                else:
                    measures = 'Drop, Cover and Hold on; If you are inside, stay inside. donot stand in the doorway. you are safe under a table. Stop driving if you are in a car. Hold on to your seat if you are at movies/stadium. remain seated so that you are not knocked down.'

            except Exception as e : 
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'

            if(len(error) == 0):
                return  render_template('success.html' , title='Disaster Classfier | Results', active_page='launch',img  = img , predictions = predictions, final_res=final_res, measures=measures)
            else:
                #return render_template('launch.html' , error = error) 
                return render_template('launch.html', title='Disaster Classfier | Launch', active_page='launch',error = error)

            
        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img , file.filename))
                img_path = os.path.join(target_img , file.filename)
                img = file.filename

                if file.filename.split('.')[-1] == 'mp4':
                    final_res = predict_from_video(img, model)
                    predictions =''
                    if final_res=="Flood":
                        measures = 'Seek Higher Grounds during Floods, and donot wait for any Instructions. Be aware of Flash flood areas such as canals, drainage channels, etc. Turn off any Electrical Appliances, and avoid driving during floods. Be ready to Evacuate.'
                    elif final_res=="Wildfire":
                        measures = 'To prevent wildfires, it is essential to undertake technical checkups regularly. have properly functioning spark arrestors. never park near dry grass, especially, close to forests. have a shovel and a fire-extinguisher. carry a bucket or anything suitable to fill with water. store a reservoir with water or sand.'
                    elif final_res=="Cyclone":
                        measures = 'Be aware of the official cyclone warning by listening to the radio or other authentic sources. Install storm shutters or board up glass windows. Keep all the doors and windows closed. Switch off the electrical mains in your house. Stay away from concrete walls and floors because thunder lightning can pass through the metal bars in them.'
                    else:
                        measures = 'Drop, Cover and Hold on; If you are inside, stay inside. donot stand in the doorway. you are safe under a table. Stop driving if you are in a car. Hold on to your seat if you are at movies/stadium. remain seated so that you are not knocked down.'
                    return  render_template('success.html' ,title='Disaster Classfier | Results', active_page='launch', img  = img , predictions = predictions, final_res=final_res, measures=measures, format='video')
                class_result , prob_result = predict(img_path , model)

                predictions = {
                      "class1":class_result[0],
                        "class2":class_result[1],
                        "class3":class_result[2],
                        "class4":class_result[3],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                        "prob4": prob_result[3]
                }
                final_res = class_result[prob_result.index(max(prob_result))]

                if final_res=="Flood":
                    measures = 'Seek Higher Grounds during Floods, and donot wait for any Instructions. Be aware of Flash flood areas such as canals, drainage channels, etc. Turn off any Electrical Appliances, and avoid driving during floods. Be ready to Evacuate.'
                elif final_res=="Wildfire":
                    measures = 'To prevent wildfires, it is essential to undertake technical checkups regularly. have properly functioning spark arrestors. never park near dry grass, especially, close to forests. have a shovel and a fire-extinguisher. carry a bucket or anything suitable to fill with water. store a reservoir with water or sand.'
                elif final_res=="Cyclone":
                    measures = 'Be aware of the official cyclone warning by listening to the radio or other authentic sources. Install storm shutters or board up glass windows. Keep all the doors and windows closed. Switch off the electrical mains in your house. Stay away from concrete walls and floors because thunder lightning can pass through the metal bars in them.'
                else:
                    measures = 'Drop, Cover and Hold on; If you are inside, stay inside. donot stand in the doorway. you are safe under a table. Stop driving if you are in a car. Hold on to your seat if you are at movies/stadium. remain seated so that you are not knocked down.'

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            if(len(error) == 0):
                return  render_template('success.html' , title='Disaster Classfier | Results', active_page='launch',img  = img , predictions = predictions, final_res=final_res, measures=measures)
            else:
                #return render_template('launch.html' , error = error) 
                return render_template('launch.html', title='Disaster Classfier | Launch', active_page='launch',error = error)

    else:
        return render_template('launch.html', title='Disaster Classfier | Launch', active_page='launch')




if __name__ == '__main__':
    app.run(debug=True)
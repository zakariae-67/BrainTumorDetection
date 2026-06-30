from flask import Flask, render_template, request, send_from_directory
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import os

#create app
app=Flask(__name__)

#load the trained model
model=load_model("models/model.h5")

#class labels
classes=["pituitary", "glioma", "notumor", "meningioma"]

#define the uploads folder
UPLOAD_FOLDER="./uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

#funtion to predict tumor type
def detect_tumor(image_path,model):
  #load images and convert it to umpy array
  IMAGE_SIZE=128
  image=load_img(image_path,target_size=(IMAGE_SIZE,IMAGE_SIZE))
  img_array=img_to_array(image)/255.0
  img_array=np.expand_dims(img_array,axis=0)

  #Make prediction using the Model
  prediction=model.predict(img_array)
  predicted_index_class=np.argmax(prediction)
  predict_label=sorted(classes)[predicted_index_class]
  confidence_score=np.max(prediction,axis=1)[0]*100

  if predict_label=="notumor":
      return "NO Tumor", confidence_score
  else:
      return f"Tumor: {predict_label}", confidence_score

#Routes
@app.route("/",methods=["GET","POST"])
def index():
    if request.method=="POST":
        # Handle file upload
        file =request.files["file"]

        if file:

            # save the file
            file_location=os.path.join(UPLOAD_FOLDER,file.filename)
            file.save(file_location)

            #predict results
            result, confidence=detect_tumor(file_location,model)

            #return results along with image path for display
            return render_template("index.html",result=result,confidence=f"{confidence:.2f}%",file_path=file_location)
    return render_template("index.html",result=None)

#Route to serve uploaded files
@app.route("/uploads/<filename>")
def get_uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"],filename)

#python main
if __name__=="__main__":
    app.run(debug=True)
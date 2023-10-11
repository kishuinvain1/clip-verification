import io
import streamlit as st
from roboflow import Roboflow
from pathlib import Path
import os
from PIL import Image
import cv2
import numpy as np
import base64





def load_image():
    opencv_image = None 
    path = None
    f = None
    uploaded_file = st.file_uploader(label='Pick an image to test')
    print(uploaded_file)
    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        opencv_image = cv2.imdecode(file_bytes, 1)
        image_data = uploaded_file.getvalue() 
        #st.image(image_data)
        name = uploaded_file.name
        path = os.path.abspath(name)
        print("abs path")
        print(path)
        opencv_image_resz = cv2.resize(opencv_image.copy(), (640,640))
        cv2.imwrite("main_image_original.jpg", opencv_image)
        cv2.imwrite("main_image.jpg", opencv_image_resz)
       
    return path, opencv_image_resz
       


	


# convert PIL Image to an RGB image( technically a numpy array ) that's compatible with opencv
def toRGB(image):
    return np.array(image)
	

	
def drawBoundingBox(saved_image ,x, y, w, h, cl, cf):
    #img = Image.open(saved_image)
    #img = cv2.imread(saved_image)
    img = saved_image
    
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)
    start_pnt = (x-w//2,y-h//2)
    end_pnt = (x+w//2, y+h//2)
    txt_start_pnt = (x-w//2, y-h//2-5)
    
    img = cv2.rectangle(img, start_pnt, end_pnt, (0,255,0), 4)
    img = cv2.putText(img, cl, txt_start_pnt, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)	
    	
    return img
    


def predict(model, url):
    return model.predict(url, confidence=40, overlap=30).json()
    #return model.predict(url, hosted=True).json()
	
	
def main():
    st.title('Tyre Classification')
    rf = Roboflow(api_key="0Uglhm9vMkjvOzEnA7t2")
    project = rf.workspace().project("tyre-classification-6icx3")
    model = project.version(1).model

     
    image, svd_img = load_image()

    result = st.button('Detect')
    if result:
        results = predict(model, svd_img)
        #results = predict(model2, url)
        print("Prediction Results are...")	
        print(results)
        if len(results['predictions']) == 0:
            st.image(svd_img)
            st.write("No Tyre Detected")
        else:
            st.write('DETECTION RESULTS')
            svd_img = cv2.cvtColor(svd_img,cv2.COLOR_BGR2RGB)
            for cnt,item in enumerate(results['predictions']):
                new_img_pth = results['predictions'][0]['image_path']
                x = results['predictions'][cnt]['x']
                y = results['predictions'][cnt]['y']
                w = results['predictions'][cnt]['width']
                h = results['predictions'][cnt]['height']
                cl = results['predictions'][cnt]['class']
                cnf = results['predictions'][cnt]['confidence']
                if 'bearing' in cl:
                    cl = cl + "&seal"
                elif 'seal' in cl:
                    continue    
                svd_img = drawBoundingBox(svd_img,x, y, w, h, cl, cnf)

            st.image(svd_img, caption='Resulting Image')    
           

if __name__ == '__main__':
    main()
